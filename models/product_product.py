# ARCHIVO: models/product_product.py
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Filtrar productos según el proveedor en órdenes de compra"""
        args = args or []
        
        # Aplicar filtro de proveedor si existe en el contexto
        args = self._apply_supplier_filter(args)
        
        # Llamar al método original
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, specification=None):
        """Sobrescribir search_read para aplicar el mismo filtro"""
        domain = domain or []
        
        # Aplicar el mismo filtro de proveedor si existe
        domain = self._apply_supplier_filter(domain)
        
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, specification=specification)
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Sobrescribir search para aplicar filtro también aquí"""
        args = self._apply_supplier_filter(args or [])
        
        # En Odoo 18, el parámetro 'count' fue removido del método search()
        # Se debe usar search_count() en su lugar
        if count:
            return super().search_count(args)
        else:
            return super().search(args, offset=offset, limit=limit, order=order)
    
    @api.model
    def web_search_read(self, domain=None, specification=None, offset=0, limit=None, 
                       order=None, count_limit=None, **kwargs):
        """Filtrar también en web_search_read que es usado por las vistas web"""
        domain = domain or []
        domain = self._apply_supplier_filter(domain)
        
        # Llamar al método padre con los parámetros correctos para Odoo 18
        return super().web_search_read(
            domain=domain, 
            specification=specification,
            offset=offset, 
            limit=limit, 
            order=order, 
            count_limit=count_limit,
            **kwargs
        )
    
    @api.model
    def _apply_supplier_filter(self, domain):
        """Método auxiliar para aplicar el filtro de proveedor"""
        # Obtener el supplier_filter del contexto
        supplier_filter = self.env.context.get('supplier_filter')
        
        # Debug para verificar el contexto
        if self.env.context.get('debug_filtering'):
            _logger.info(f"Aplicando filtro de proveedor: {supplier_filter}")
            _logger.info(f"Contexto completo: {dict(self.env.context)}")
        
        if supplier_filter:
            # Si es una tupla (id, name), extraer solo el ID
            if isinstance(supplier_filter, (tuple, list)) and len(supplier_filter) >= 2:
                supplier_id = supplier_filter[0]
            else:
                supplier_id = supplier_filter
            
            try:
                # Buscar templates autorizados para este proveedor
                authorized_templates = self.env['product.template'].search([
                    ('supplier_ids', '=', supplier_id),
                    ('purchase_ok', '=', True)
                ])
                
                if authorized_templates:
                    # Obtener todos los productos (variantes) de estos templates
                    authorized_product_ids = authorized_templates.mapped('product_variant_ids.id')
                    domain = domain + [('id', 'in', authorized_product_ids)]
                    
                    if self.env.context.get('debug_filtering'):
                        _logger.info(f"Productos autorizados encontrados: {len(authorized_product_ids)}")
                else:
                    # Si no hay productos autorizados, no mostrar ninguno
                    domain = domain + [('id', 'in', [])]
                    
                    if self.env.context.get('debug_filtering'):
                        _logger.info("No se encontraron productos autorizados para este proveedor")
                        
            except Exception as e:
                _logger.error(f"Error aplicando filtro de proveedor: {e}")
                # En caso de error, no filtrar para evitar romper la funcionalidad
                pass
        
        return domain