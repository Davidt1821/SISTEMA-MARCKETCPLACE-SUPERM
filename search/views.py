from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .querysets import comparison_products_queryset, search_products_queryset
from .serializers import ProductComparisonSerializer, SearchProductSerializer


class SearchProductsView(APIView):
    def get(self, request):
        queryset = search_products_queryset(request.query_params)
        serializer = SearchProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CompareProductPricesView(APIView):
    def get(self, request):
        query = (request.query_params.get('q') or '').strip()
        if not query:
            return Response({'detail': 'Informe o parametro q.'}, status=status.HTTP_400_BAD_REQUEST)

        results = comparison_products_queryset(query)
        serializer = ProductComparisonSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
