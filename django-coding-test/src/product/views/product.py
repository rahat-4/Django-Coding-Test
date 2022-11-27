from django.views import generic
from django.db.models import Q
from django.db.models import Max
from django.db.models import FloatField
from django.shortcuts import render, redirect

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from product import serializers
from product.forms import ProductForm


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

class PostProductView(APIView):
    def post(self, request):
        p_data = request.data
        
        # product_images_data = p_data.pop('product_image')
        product_variants_data = p_data.pop('product_variant')
        product_variant_prices_data = p_data.pop('product_variant_prices')
        product_data = p_data
        
        product = serializers.ProductSerializer(data=product_data)
        
        if product.is_valid():
            product.save()
            
            pv_price = []
            v_data = {}
            for pv in product_variants_data:
                for p in pv['tags']:
                    v_data['variant_title'] = p
                    v_data['variant']= pv['option']
                    v_data['product'] = product.data['id']
                    
                    product_variant = serializers.ProductVariantSerializer(data=v_data)
                        
                    if product_variant.is_valid():
                        product_variant.save()
                        pv_price.append(product_variant.data)
                    else:
                        print("Failed ", product_variant.data)
                        print("Error ", product_variant.errors)
            
            pvp_data = {}
            for pvp in product_variant_prices_data:
                one = pvp['title'].split('/')[0]
                two = pvp['title'].split('/')[1]
                three = pvp['title'].split('/')[2]

                for p in pv_price:
                    if p['variant_title'] == one:
                        one = p['id']
                    if p['variant_title'] == two:
                        two = p['id']
                    if p['variant_title'] == three:
                        three = p['id']

                pvp_data['product_variant_one'] = one
                pvp_data['product_variant_two'] = two
                pvp_data['product_variant_three'] = three
                
                pvp_data['price'] = pvp['price']
                pvp_data['stock'] = pvp['stock']
                pvp_data['product'] = product.data['id']
                
            
                product_variant_price = serializers.ProductVariantPriceSerializer(data=pvp_data)
                
                if product_variant_price.is_valid():
                    product_variant_price.save()
                else:
                    print(product_variant_price.errors)
                    print(product_variant_price.data)

            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ProductListView(generic.ListView):
    model = Product
    template_name='products/list.html'
    paginate_by = 2
    
    def get_queryset(self):
        if self.request.method == 'GET':
            #search results for product
            product_search = self.request.GET.get('title','')
            search_by_date = self.request.GET.get('date','')

            #search results for variant
            variant_search = self.request.GET.get('variant','')
            min_price = self.request.GET.get('price_from',0)
            max_price = self.request.GET.get('price_to',0)
            
            if max_price == 0 or max_price == '':
                max_price = ProductVariantPrice.objects.aggregate(Max('price', output_field=FloatField()))['price__max']
            if min_price == '':
                min_price = 0

            product_var_price = ProductVariantPrice.objects.filter(price__range=(min_price, max_price))
            product_var = ProductVariant.objects.filter(variant_title__icontains=variant_search)
            
            product_list = Product.objects.filter(Q(title__icontains=product_search) & Q(created_at__contains=search_by_date) & Q(product_variants__in=product_var) & Q(product_variant_prices__in=product_var_price)).distinct()

        return product_list

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['variant_list'] = Variant.objects.order_by('title')
                          
        return context

def edit_product(request, pk):
    product = Product.objects.get(id=pk)
    product_form = ProductForm(instance=product)
    
    
    if request.method == "POST":
        product_form = ProductForm(request.POST, instance=product)
        if product_form.is_valid():
            product_form.save()
            
            return redirect("product:list.product")
    dict = { 'product_form': product_form}
    return render(request, "products/edit.html", dict)