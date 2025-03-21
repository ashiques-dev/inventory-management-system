from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from inventory.models import Item
from inventory.serializer import ItemSerializer
from inventory.utils import UserAuth
from django.core.files.storage import default_storage
from django.core.cache import cache
import logging
from rest_framework import generics
# Create your views here.

logger = logging.getLogger(__name__)
logger_inventory = logging.getLogger('inventory')


class InventoryListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    permission_classes = [UserAuth]
    serializer_class = ItemSerializer


class InventoryUpdateDeleteView(APIView):
    permission_classes = [UserAuth]

    def get_item(self, id):
        try:
            item = Item.objects.get(id=id)
        except Item.DoesNotExist:
            logger_inventory.warning(f"Item {id} not found.")
            return None
        return item

    def get(self, request, id):

        cache_key = f'item_{id}'
        item = cache.get(cache_key)

        if not item:

            item = self.get_item(id)
            if item is None:
                return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
            # caching data for 10 minutes
            cache.set(cache_key, item, timeout=60*10)

        serializer = ItemSerializer(item)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, id):
        item = self.get_item(id)
        if item is None:
            return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_item = serializer.save()

        cache_key = f'item_{id}'
        cache.set(cache_key, ItemSerializer(updated_item).data, timeout=60)

        return Response({"message": "Item updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        item = self.get_item(id)
        if item is None:
            return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        if item.image:
            default_storage.delete(item.image.path)
        item.delete()

        cache_key = f'item_{id}'
        cache.delete(cache_key)
        return Response({'message': 'item deleted'}, status=status.HTTP_204_NO_CONTENT)
