{
    'name': 'Catálogo Productos Proveedores Hexágonos',
    'version': '18.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Gestión de catálogo productos por proveedor en órdenes de compra',
    'description': """
        Módulo que permite:
        - Ligar productos específicos con proveedores
        - Filtrar automáticamente productos por proveedor en órdenes de compra
        - Gestión de catálogo productos-proveedores
    """,
    'author': 'Alphaqueb Consulting SAS',
    'depends': ['base', 'product', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'catalogo_productos_proveedores_hexagonos/static/src/js/purchase_order.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}