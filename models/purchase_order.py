from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.onchange('partner_id')
    def _onchange_partner_id_filter_products(self):
        """Filtrar productos cuando cambia el proveedor"""
        # Llamar al método original si existe
        result = {}
        if hasattr(super(), '_onchange_partner_id'):
            result = super()._onchange_partner_id() or {}
        
        if self.partner_id:
            # Verificar si hay líneas existentes con productos no autorizados
            lines_to_remove = []
            for line in self.order_line:
                if (line.product_id and 
                    line.product_id.product_tmpl_id.supplier_ids and
                    self.partner_id not in line.product_id.product_tmpl_id.supplier_ids):
                    lines_to_remove.append(line.product_id.name)
            
            # Si hay productos no autorizados, avisar al usuario
            if lines_to_remove:
                return {
                    'warning': {
                        'title': 'Productos no autorizados',
                        'message': f'Algunos productos no están autorizados para el proveedor {self.partner_id.name}: {", ".join(lines_to_remove[:3])}{"..." if len(lines_to_remove) > 3 else ""}. Se recomienda revisar las líneas de la orden.'
                    }
                }
        
        return result