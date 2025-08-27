/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

// Patch para el campo Many2One de productos en órdenes de compra
patch(Many2OneField.prototype, {
    
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
    },

    /**
     * Modificar el contexto y dominio para productos en órdenes de compra
     */
    get context() {
        const context = super.context;
        
        // Solo aplicar en órdenes de compra y para el campo product_id
        if (this.props.name === "product_id" && 
            this.props.record?.resModel === "purchase.order.line") {
            
            const parentRecord = this.props.record.model.root.data;
            const supplierId = parentRecord.partner_id;
            
            if (supplierId) {
                context.supplier_filter = supplierId;
                context.debug_filtering = true;
                
                // Log para debug
                console.log("Aplicando filtro de proveedor:", supplierId);
            }
        }
        
        return context;
    },

    /**
     * Modificar el dominio para filtrar productos
     */
    get domain() {
        let domain = super.domain || [];
        
        // Solo aplicar en órdenes de compra y para el campo product_id
        if (this.props.name === "product_id" && 
            this.props.record?.resModel === "purchase.order.line") {
            
            // Asegurar que solo se muestren productos de compra
            domain = [...domain, ["purchase_ok", "=", true]];
            
            const parentRecord = this.props.record.model.root.data;
            const supplierId = parentRecord.partner_id;
            
            if (supplierId) {
                // El filtrado se maneja en el backend, pero podemos agregar
                // un dominio adicional aquí si es necesario
                console.log("Dominio aplicado con proveedor:", supplierId);
            }
        }
        
        return domain;
    },

    /**
     * Interceptar la selección de productos para validación adicional
     */
    async _onSelectionChanged(value) {
        const result = await super._onSelectionChanged(value);
        
        // Validación adicional en el frontend
        if (this.props.name === "product_id" && 
            this.props.record?.resModel === "purchase.order.line" && 
            value) {
            
            const parentRecord = this.props.record.model.root.data;
            const supplierId = parentRecord.partner_id;
            
            if (supplierId) {
                try {
                    // Verificar si el producto está autorizado
                    const authorizedProducts = await this.orm.call(
                        'product.template',
                        'get_products_by_supplier',
                        [supplierId[0]]
                    );
                    
                    const isAuthorized = authorizedProducts.some(p => p.id === value[0]);
                    
                    if (!isAuthorized) {
                        this.notification.add(
                            `El producto seleccionado no está autorizado para el proveedor ${supplierId[1]}`,
                            { type: 'warning' }
                        );
                    }
                } catch (error) {
                    console.error("Error validando producto:", error);
                }
            }
        }
        
        return result;
    }
});

// Patch específico para el comportamiento de búsqueda en Many2One
import { Many2OnePopup } from "@web/views/fields/many2one/many2one_popup/many2one_popup";

patch(Many2OnePopup.prototype, {
    
    setup() {
        super.setup();
        
        // Asegurar que el contexto se pase correctamente al popup
        if (this.props.context && this.props.context.supplier_filter) {
            console.log("Popup Many2One con filtro de proveedor:", this.props.context.supplier_filter);
        }
    },

    get searchProps() {
        const props = super.searchProps;
        
        // Mantener el contexto en las props de búsqueda
        if (this.props.context?.supplier_filter) {
            props.context = {
                ...props.context,
                supplier_filter: this.props.context.supplier_filter,
                debug_filtering: true
            };
            
            console.log("SearchProps con contexto:", props.context);
        }
        
        return props;
    }
});