# -*- coding: utf-8 -*-
# from odoo import http


# class Nutrete(http.Controller):
#     @http.route('/nutrete/nutrete', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nutrete/nutrete/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nutrete.listing', {
#             'root': '/nutrete/nutrete',
#             'objects': http.request.env['nutrete.nutrete'].search([]),
#         })

#     @http.route('/nutrete/nutrete/objects/<model("nutrete.nutrete"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nutrete.object', {
#             'object': obj
#         })
