from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class Dieta(models.Model):
    _name = 'nutrete.dieta'
    _description = 'Registro de Dietas'

    nombre_dieta = fields.Char(string="Nombre", required=True, default="Dieta")
    dietista_id = fields.Many2one('res.partner', string="Dietista", required=True, domain=[('is_dietista', '=', True)])
    nutricionista_id = fields.Many2one('res.partner', string="Nutricionista", required=True, domain=[('is_nutricionista', '=', True)])
    cliente_id = fields.Many2one('res.partner', string="Cliente", required=True, domain=[('is_client', '=', True)])
    nivel_actividad = fields.Selection([
        ('1', 'Poca'),
        ('2', 'Normal'),
        ('3', 'Mucha')
    ], string='Nivel de Actividad Física', required=True, default='1')
    consumo_calorias = fields.Char(string="Consumo Calórico Diario", compute="_calcular_calorias", store=True)
    revisiones_ids = fields.One2many('nutrete.revision', 'dieta_id', string="Revisiones")

    @api.depends('cliente_id', 'nivel_actividad')
    def _calcular_calorias(self):
        for record in self:
            if record.cliente_id and record.nivel_actividad:
                cliente = record.cliente_id
                if cliente.sexo == "Hombre":
                    geb = 66.47 + (13.75 * cliente.peso_kg) + (5 * cliente.altura_m * 100) - (6.74 * cliente.edad)
                else:
                    geb = 655.1 + (9.56 * cliente.peso_kg) + (1.85 * cliente.altura_m * 100) - (4.68 * cliente.edad)
                fb = {
                    '1': 1.3,
                    '2': 1.55,
                    '3': 1.9,
                }.get(record.nivel_actividad, 1.0)
                record.consumo_calorias = str(geb * fb)
            else:
                record.consumo_calorias = '0'

class Revision(models.Model):
    _name = 'nutrete.revision'
    _description = 'Registro de Revisiones'

    nombre_revision = fields.Char(string="Nombre", required=True, default="Revisión")
    fecha_revision = fields.Datetime(string="Fecha y Hora", required=True)
    dieta_id = fields.Many2one('nutrete.dieta', string="Dieta", required=True)
    peso_actual = fields.Integer(string="Peso Actual (kg)", required=True)
    comentarios_revision = fields.Text(string="Comentarios")
    evolucion_revision = fields.Text(string="Evolución")

class Taller(models.Model):
    _name = 'nutrete.taller'
    _description = 'Registro de Talleres y Charlas'

    nombre_taller = fields.Char(string="Nombre", required=True, default="Taller")
    profesionales_ids = fields.Many2many('res.partner', string="Dietistas y Nutricionistas", required=True)
    fecha_taller = fields.Datetime(string="Fecha y Hora", required=True)
    enlace_taller = fields.Char(string="Enlace", required=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_client = fields.Boolean(string='Es Cliente')
    is_dietista = fields.Boolean(string='Es Dietista')
    is_nutricionista = fields.Boolean(string='Es Nutricionista')

    identificacion = fields.Char(string="Identificación", required=True)
    especialidad_dietista = fields.Char(string="Especialidad Dietista")
    especialidad_nutricionista = fields.Char(string="Especialidad Nutricionista")
    sexo = fields.Selection([
        ('Hombre', 'Hombre'),
        ('Mujer', 'Mujer')
    ], string='Sexo', required=True)
    historial_medico = fields.Text(string="Historial Médico", required=True)
    motivo_consulta = fields.Text(string="Motivo de la Consulta", required=True)
    edad = fields.Integer(string="Edad")
    peso_kg = fields.Integer(string="Peso (kg)")
    altura_m = fields.Float(string="Altura (metros)")
    indice_grasa_corporal = fields.Float(string="Índice de Grasa Corporal", compute="_calcular_grasa_corporal", store=True)
    dietas_ids = fields.One2many('nutrete.dieta', 'cliente_id', string="Dietas Asignadas")

    @api.depends('peso_kg', 'altura_m', 'sexo', 'edad')
    def _calcular_grasa_corporal(self):
        for record in self:
            if record.peso_kg > 0 and record.altura_m > 0:  # Comprobación para evitar división por cero
                imc = record.peso_kg / (record.altura_m ** 2)
                if record.sexo == "Hombre":
                    record.indice_grasa_corporal = 1.2 * imc + 0.23 * record.edad - 10.8 - 5.4
                else:
                    record.indice_grasa_corporal = 1.2 * imc + 0.23 * record.edad - 5.4
            else:
                record.indice_grasa_corporal = 0.0  # Asignar un valor predeterminado si altura_m es cero

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.is_client:
            category = self.env['res.partner.category'].search([('name', '=', 'Cliente')], limit=1)
            if not category:
                category = self.env['res.partner.category'].create({'name': 'Cliente'})
            res.category_id = [(4, category.id)]
        if res.is_dietista:
            category = self.env['res.partner.category'].search([('name', '=', 'Dietista')], limit=1)
            if not category:
                category = self.env['res.partner.category'].create({'name': 'Dietista'})
            res.category_id = [(4, category.id)]
        if res.is_nutricionista:
            category = self.env['res.partner.category'].search([('name', '=', 'Nutricionista')], limit=1)
            if not category:
                category = self.env['res.partner.category'].create({'name': 'Nutricionista'})
            res.category_id = [(4, category.id)]
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for record in self:
            if 'is_client' in vals and vals['is_client']:
                category = self.env['res.partner.category'].search([('name', '=', 'Cliente')], limit=1)
                if not category:
                    category = self.env['res.partner.category'].create({'name': 'Cliente'})
                record.category_id = [(4, category.id)]
            if 'is_dietista' in vals and vals['is_dietista']:
                category = self.env['res.partner.category'].search([('name', '=', 'Dietista')], limit=1)
                if not category:
                    category = self.env['res.partner.category'].create({'name': 'Dietista'})
                record.category_id = [(4, category.id)]
            if 'is_nutricionista' in vals and vals['is_nutricionista']:
                category = self.env['res.partner.category'].search([('name', '=', 'Nutricionista')], limit=1)
                if not category:
                    category = self.env['res.partner.category'].create({'name': 'Nutricionista'})
                record.category_id = [(4, category.id)]
        return res

    @api.constrains('identificacion')
    def _validar_identificacion(self):
        for record in self:
            if not self._validar_dni(record.identificacion):
                raise ValidationError("Identificación inválida.")

    @staticmethod
    def _validar_dni(dni):
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        dni_regex = re.compile(r'^[0-9]{8}[A-Z]$')
        if dni_regex.match(dni):
            numero = int(dni[:-1])
            letra = dni[-1]
            if letras[numero % 23] == letra:
                return True
        return False
