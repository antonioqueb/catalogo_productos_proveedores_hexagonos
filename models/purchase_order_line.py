# ARCHIVO: models/purchase_order_line.py
from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.onchange('product_id')
    def _onchange_product_id_check_supplier(self):
        """Validar que el producto esté autorizado para el proveedor"""
        if self.product_id and self.order_id and self.order_id.partner_id:
            # Verificar si el producto tiene proveedores configurados
            supplier_ids = self.product_id.product_tmpl_id.supplier_ids
            
            if supplier_ids:
                # Verificar si el proveedor actual está autorizado
                current_supplier = self.order_id.partner_id
                
                # Incluir empresa padre si existe
                authorized_suppliers = supplier_ids
                if current_supplier.parent_id:
                    authorized_suppliers |= supplier_ids.filtered(lambda s: s.id == current_supplier.parent_id.id)
                
                if current_supplier not in authorized_suppliers:
                    # Guardar el nombre del producto antes de limpiarlo
                    product_name = self.product_id.name
                    product_code = self.product_id.default_code or ''
                    
                    # Obtener lista de proveedores autorizados
                    authorized_names = authorized_suppliers.mapped('name')
                    
                    # Limpiar el producto seleccionado
                    self.product_id = False
                    
                    # Mensaje más detallado
                    message = f'El producto "{product_code} {product_name}" no está autorizado para el proveedor {current_supplier.name}.\n\n'
                    message += f'Proveedores autorizados para este producto:\n• ' + '\n• '.join(authorized_names)
                    
                    # Retornar advertencia
                    return {
                        'warning': {
                            'title': 'Producto no autorizado',
                            'message': message
                        }
                    }
