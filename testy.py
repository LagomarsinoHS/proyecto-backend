data = {
    'factura': {
        'folio': '99', 
        'fecha_emision': '27-07-2020', 
        'fecha_recepcion': '27-07-2020', 
        'monto_neto': '10000', 
        'monto_iva': '1900', 
        'monto_otros_impuestos': '', 
        'monto_total': '11900', 
        'proveedor_id': '4', 
        'entradas_inventario': [
            {
                'cantidad': '1', 
                'precio_costo_unitario': '1500', 
                'costo_total': 1500, 
                'usuario_id': 1, 
                'producto_id': '1'
            }, 
            {
                
                'cantidad': '2', 
                'precio_costo_unitario': '1000', 
                'costo_total': 2000, 
                'usuario_id': 1, 
                'producto_id': '2'
            }
        ]
    }, 
    'detalleEntrada': {
        'cantidad': None, 
        'precio_costo_unitario': None, 
        'costo_total': None, 
        'usuario_id': 1, 
        'producto_id': None
    }
}
print(data['factura']['folio'])

data1 = {
    'id': 13, 
    'folio': 445, 
    'fecha_emision': '2020-07-28', 
    'fecha_recepcion': '2020-07-28', 
    'monto_neto': 20000, 
    'monto_iva': 3800, 
    'monto_otros_impuestos': 0, 
    'monto_total': 23800, 
    'proveedor_id': 4, 
    'entradas_inventario': [
        {
            'id': 19, 
            'cantidad': 2, 
            'precio_costo_unitario': 5000, 
            'costo_total': 10000, 
            'fecha_registro': 'Tue, 28 Jul 2020 12:54:19 GMT', 
            'usuario_id': 1, 
            'factura_compra_id': 13, 
            'producto_id': 3, 
            'producto': {
                'id': 3, 
                'sku': 'yrt67', 
                'descripcion': 'Carne', 
                'codigo_barra': '6456', 
                'unidad_entrega': 'unidad', 
                'categoria_id': 1, 
                'precio_venta_unitario': 5000, 
                'margen_contribucion': 0.1
                }
        }, 
        {
            'id': 20, 
            'cantidad': 100, 
            'precio_costo_unitario': 100, 
            'costo_total': 10000, 
            'fecha_registro': 'Tue, 28 Jul 2020 12:54:19 GMT', 
            'usuario_id': 1, 
            'factura_compra_id': 13, 
            'producto_id': 8, 
            'producto': {
                'id': 8, 
                'sku': '65645te', 
                'descripcion': 'Chicle Menta', 
                'codigo_barra': '453453', 
                'unidad_entrega': 'unidad', 
                'categoria_id': 1, 
                'precio_venta_unitario': 300, 
                'margen_contribucion': 0.1
            }
        }
    ]
}