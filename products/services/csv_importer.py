import csv
import io
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction

from prices.models import ProductPrice
from promotions.models import Promotion
from products.models import Category, Product
from supermarkets.models import Supermarket


REQUIRED_COLUMNS = {
    'supermarket_name',
    'category_name',
    'product_name',
    'price',
}

PLACEHOLDER_TEXT = 'Nao informado'


class CSVImportError(Exception):
    pass


@dataclass
class ParsedRow:
    supermarket_name: str
    supermarket_cnpj: str | None
    category_name: str
    product_name: str
    brand: str
    barcode: str | None
    description: str
    price: Decimal
    old_price: Decimal | None
    available: bool
    promotion_price: Decimal | None
    promotion_start: date | None
    promotion_end: date | None


def import_products_csv(file):
    _validate_file_extension(file.name)

    try:
        decoded_content = file.read().decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise CSVImportError('O arquivo CSV deve estar em UTF-8.') from exc

    reader = csv.DictReader(io.StringIO(decoded_content))
    _validate_columns(reader.fieldnames)

    summary = {
        'created_products': 0,
        'updated_products': 0,
        'created_prices': 0,
        'updated_prices': 0,
        'created_promotions': 0,
        'errors': [],
    }

    for line_number, row in enumerate(reader, start=2):
        row = _normalize_row_keys(row)
        if _is_empty_row(row):
            continue

        try:
            parsed_row = _parse_row(row)
            with transaction.atomic():
                supermarket = _get_or_create_supermarket(parsed_row)
                category = _get_or_create_category(parsed_row.category_name)
                product, product_created, product_updated = _get_or_create_product(parsed_row, category)
                price_created, price_updated = _create_or_update_price(parsed_row, product, supermarket)
                promotion_created = _create_promotion_if_needed(parsed_row, product, supermarket)
        except Exception as exc:
            summary['errors'].append({
                'line': line_number,
                'message': str(exc),
            })
            continue

        if product_created:
            summary['created_products'] += 1
        elif product_updated:
            summary['updated_products'] += 1

        if price_created:
            summary['created_prices'] += 1
        elif price_updated:
            summary['updated_prices'] += 1

        if promotion_created:
            summary['created_promotions'] += 1

    return summary


def _validate_file_extension(file_name):
    if not file_name.lower().endswith('.csv'):
        raise CSVImportError('Envie um arquivo com extensao .csv.')


def _validate_columns(fieldnames):
    if not fieldnames:
        raise CSVImportError('O arquivo CSV esta vazio ou sem cabecalho.')

    normalized = {field.strip() for field in fieldnames if field}
    missing = sorted(REQUIRED_COLUMNS - normalized)
    if missing:
        raise CSVImportError(f'Colunas obrigatorias ausentes: {", ".join(missing)}.')


def _is_empty_row(row):
    return not any((value or '').strip() for value in row.values())


def _normalize_row_keys(row):
    normalized_row = {}
    for key, value in row.items():
        normalized_key = key.strip() if isinstance(key, str) else key
        normalized_row[normalized_key] = value
    return normalized_row


def _parse_row(row):
    supermarket_name = _require_value(row, 'supermarket_name')
    category_name = _require_value(row, 'category_name')
    product_name = _require_value(row, 'product_name')

    promotion_price_raw = _clean_value(row.get('promotion_price'))
    promotion_start_raw = _clean_value(row.get('promotion_start'))
    promotion_end_raw = _clean_value(row.get('promotion_end'))

    promotion_price = _parse_decimal(promotion_price_raw, 'promotion_price') if promotion_price_raw else None
    promotion_start = _parse_date(promotion_start_raw, 'promotion_start') if promotion_start_raw else None
    promotion_end = _parse_date(promotion_end_raw, 'promotion_end') if promotion_end_raw else None

    if promotion_price is not None and (promotion_start is None or promotion_end is None):
        raise ValueError('promotion_start e promotion_end sao obrigatorios quando promotion_price for informado.')

    if promotion_start and promotion_end and promotion_end < promotion_start:
        raise ValueError('promotion_end deve ser maior ou igual a promotion_start.')

    return ParsedRow(
        supermarket_name=supermarket_name,
        supermarket_cnpj=_clean_value(row.get('supermarket_cnpj')),
        category_name=category_name,
        product_name=product_name,
        brand=_clean_value(row.get('brand')) or '',
        barcode=_clean_value(row.get('barcode')),
        description=_clean_value(row.get('description')) or '',
        price=_parse_decimal(_require_value(row, 'price'), 'price'),
        old_price=_parse_decimal(_clean_value(row.get('old_price')), 'old_price') if _clean_value(row.get('old_price')) else None,
        available=_parse_boolean(_clean_value(row.get('available'))),
        promotion_price=promotion_price,
        promotion_start=promotion_start,
        promotion_end=promotion_end,
    )


def _require_value(row, column):
    value = _clean_value(row.get(column))
    if not value:
        raise ValueError(f'O campo {column} e obrigatorio.')
    return value


def _clean_value(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _parse_decimal(value, field_name):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f'Valor invalido para {field_name}: {value}.') from exc


def _parse_boolean(value):
    if value is None:
        return True

    normalized = _normalize_text(value)
    accepted_true = {'true', '1', 'sim', 's', 'yes'}
    accepted_false = {'false', '0', 'nao', 'n', 'no'}

    if normalized in accepted_true:
        return True
    if normalized in accepted_false:
        return False
    raise ValueError(f'Valor invalido para available: {value}.')


def _normalize_text(value):
    normalized = unicodedata.normalize('NFKD', value.strip().lower())
    return ''.join(character for character in normalized if not unicodedata.combining(character))


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'Data invalida para {field_name}: {value}. Use o formato YYYY-MM-DD.') from exc


def _get_or_create_category(category_name):
    category, _ = Category.objects.get_or_create(
        name=category_name,
        defaults={'is_active': True},
    )
    return category


def _get_or_create_supermarket(parsed_row):
    queryset = Supermarket.objects.all()

    if parsed_row.supermarket_cnpj:
        supermarket = queryset.filter(cnpj=parsed_row.supermarket_cnpj).first()
    else:
        supermarket = queryset.filter(name__iexact=parsed_row.supermarket_name).first()

    if supermarket:
        changed = False
        if supermarket.name != parsed_row.supermarket_name:
            supermarket.name = parsed_row.supermarket_name
            changed = True
        if parsed_row.supermarket_cnpj and supermarket.cnpj != parsed_row.supermarket_cnpj:
            supermarket.cnpj = parsed_row.supermarket_cnpj
            changed = True
        if changed:
            supermarket.save(update_fields=['name', 'cnpj'])
        return supermarket

    return Supermarket.objects.create(
        name=parsed_row.supermarket_name,
        cnpj=parsed_row.supermarket_cnpj,
        address=PLACEHOLDER_TEXT,
        district=PLACEHOLDER_TEXT,
        city=PLACEHOLDER_TEXT,
        is_active=True,
    )


def _get_or_create_product(parsed_row, category):
    if parsed_row.barcode:
        product = Product.objects.filter(barcode=parsed_row.barcode).first()
    else:
        product = Product.objects.filter(
            name__iexact=parsed_row.product_name,
            brand__iexact=parsed_row.brand,
        ).first()

    if not product:
        product = Product.objects.create(
            name=parsed_row.product_name,
            brand=parsed_row.brand,
            category=category,
            barcode=parsed_row.barcode,
            description=parsed_row.description,
            is_active=True,
        )
        return product, True, False

    changed = False
    if product.name != parsed_row.product_name:
        product.name = parsed_row.product_name
        changed = True
    if product.brand != parsed_row.brand:
        product.brand = parsed_row.brand
        changed = True
    if product.category_id != category.id:
        product.category = category
        changed = True
    if parsed_row.description and product.description != parsed_row.description:
        product.description = parsed_row.description
        changed = True
    if parsed_row.barcode and product.barcode != parsed_row.barcode:
        product.barcode = parsed_row.barcode
        changed = True

    if changed:
        product.save()

    return product, False, changed


def _create_or_update_price(parsed_row, product, supermarket):
    price_obj = ProductPrice.objects.filter(product=product, supermarket=supermarket).first()
    if not price_obj:
        ProductPrice.objects.create(
            product=product,
            supermarket=supermarket,
            price=parsed_row.price,
            old_price=parsed_row.old_price,
            available=parsed_row.available,
        )
        return True, False

    changed = False
    if price_obj.price != parsed_row.price:
        price_obj.price = parsed_row.price
        changed = True
    if price_obj.old_price != parsed_row.old_price:
        price_obj.old_price = parsed_row.old_price
        changed = True
    if price_obj.available != parsed_row.available:
        price_obj.available = parsed_row.available
        changed = True

    if changed:
        price_obj.save()

    return False, changed


def _create_promotion_if_needed(parsed_row, product, supermarket):
    if parsed_row.promotion_price is None:
        return False

    promotion, created = Promotion.objects.get_or_create(
        product=product,
        supermarket=supermarket,
        promotional_price=parsed_row.promotion_price,
        start_date=parsed_row.promotion_start,
        end_date=parsed_row.promotion_end,
        defaults={
            'description': parsed_row.description,
            'is_active': True,
        },
    )

    if not created:
        changed = False
        if promotion.description != parsed_row.description:
            promotion.description = parsed_row.description
            changed = True
        if not promotion.is_active:
            promotion.is_active = True
            changed = True
        if changed:
            promotion.save()

    return created
