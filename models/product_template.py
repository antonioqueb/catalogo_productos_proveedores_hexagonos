from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    supplier_ids = fields.Many2many(
        'res.partner',
        'product_supplier_rel',
        'product_tmpl_id',
        'supplier_id',
        string='Proveedores Autorizados',
        domain=[('is_company', '=', True)],  # Removido supplier_rank > 0
        help='Proveedores autorizados para este producto'
    )
    
    # NUEVO: Campo para contar proveedores (para el botón inteligente)
    supplier_count = fields.Integer(
        'Número de Proveedores', 
        compute='_compute_supplier_count',
        store=False
    )
    
    @api.depends('supplier_ids')
    def _compute_supplier_count(self):
        """Calcula el número de proveedores autorizados"""
        for product in self:
            product.supplier_count = len(product.supplier_ids)
    
    @api.model
    def get_products_by_supplier(self, supplier_id):
        """Obtiene productos disponibles para un proveedor específico"""
        if not supplier_id:
            return []
        
        products = self.search([
            ('supplier_ids', 'in', [supplier_id]),
            ('purchase_ok', '=', True)
        ])
        
        return products.mapped(lambda p: {
            'id': p.id,
            'name': p.name,
            'default_code': p.default_code or '',
            'uom_id': p.uom_po_id.id if p.uom_po_id else p.uom_id.id,
            'uom_name': p.uom_po_id.name if p.uom_po_id else p.uom_id.name,
        })