# Marketplace para Supermercados

Backend inicial em Python, Django, Django REST Framework e PostgreSQL para consulta de produtos, precos e promocoes de supermercados.

## Tecnologias

- Python
- Django
- Django REST Framework
- PostgreSQL
- django-filter
- Pillow
- python-decouple

## Configuracao local

1. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Crie um banco PostgreSQL:

```sql
CREATE DATABASE marketplace_db;
```

4. Crie o arquivo de ambiente:

```bash
copy .env.example .env
```

5. Ajuste o `.env` com os dados do seu PostgreSQL.

6. Rode as migrations:

```bash
python manage.py migrate
```

7. Crie um superusuario:

```bash
python manage.py createsuperuser
```

8. Inicie o servidor:

```bash
python manage.py runserver
```

## Admin

- Painel: `http://127.0.0.1:8000/admin/`
- Importacao CSV: `http://127.0.0.1:8000/admin/importar-csv/`

## Importacao CSV

Cabecalho esperado:

```text
supermarket_name,supermarket_cnpj,category_name,product_name,brand,barcode,description,price,old_price,available,promotion_price,promotion_start,promotion_end
```

Exemplo:

```csv
Supermercado Central,00000000000100,Alimentos,Arroz Tipo 1 5kg,Tio Joao,7891000100103,Arroz branco tipo 1 pacote 5kg,24.90,27.90,true,,,
Supermercado Central,00000000000100,Alimentos,Feijao Carioca 1kg,Camil,7896006711115,Feijao carioca pacote 1kg,8.99,10.50,true,7.99,2026-04-27,2026-05-05
```

Como importar pelo Django Admin:

1. Acesse `/admin/` ou `/admin/importar-csv/`.
2. Selecione o arquivo `.csv`.
3. Envie o arquivo.
4. Confira o resumo da importacao e os erros por linha.

## API publica

### Busca de produtos

```text
GET /api/search/?q=arroz
GET /api/search/?q=arroz&city=Nova Serrana
GET /api/search/?category=Alimentos
GET /api/search/?supermarket=Supermercado Central
GET /api/search/?brand=Tio Joao
GET /api/search/?barcode=7891000100103
GET /api/search/?available=true
```

Filtros suportados em `/api/search/`:

```text
q
category
brand
city
supermarket
barcode
available
```

A busca considera:

- nome do produto
- marca
- codigo de barras
- categoria

O retorno evita duplicidade de produtos e ordena pelo menor preco efetivo.

### Comparacao de precos

```text
GET /api/compare/?q=arroz
```

O endpoint retorna:

- produto encontrado
- marca
- categoria
- codigo de barras
- menor preco encontrado
- lista de supermercados com preco ordenada do menor para o maior
- preco atual considerando promocao valida
- preco original
- preco antigo
- disponibilidade
- indicador de promocao ativa

### Promocoes ativas

```text
GET /api/promotions/
GET /api/promotions/?city=Nova Serrana
GET /api/promotions/?category=Alimentos
```

O endpoint retorna somente promocoes ativas e dentro da data valida.

### Precos de um produto

```text
GET /api/products/1/prices/
```

O endpoint retorna todos os supermercados com preco cadastrado para o produto, incluindo promocao ativa e ordenacao pelo menor preco efetivo.

## Frontend publico

Rotas publicas disponiveis:

```text
GET /
GET /buscar/?q=arroz
GET /comparar/?q=arroz
GET /promocoes/
```

O frontend foi construido com templates Django tradicionais e CSS simples, sem React ou framework externo.

Paginas:

- `/` mostra busca principal, categorias e promocoes em destaque.
- `/buscar/?q=arroz` mostra produtos encontrados com menor preco e link para comparacao.
- `/comparar/?q=arroz` mostra supermercados, preco atual, preco antigo, promocao valida e disponibilidade.
- `/promocoes/` lista promocoes ativas dentro do periodo valido.
