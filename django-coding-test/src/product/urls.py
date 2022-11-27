from django.urls import path

from product.views.product import CreateProductView, ProductListView, PostProductView, edit_product
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"


urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    path('product-post', PostProductView.as_view(), name='post.product'),
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', ProductListView.as_view(), name='list.product'),
    path('edit/<int:pk>', edit_product, name='edit.product'),
]