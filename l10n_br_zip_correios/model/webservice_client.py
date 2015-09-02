# -*- encoding: utf-8 -*-
##############################################################################
#
#    Address from Brazilian Localization ZIP by Correios to Odoo
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Michell Stuttgart <michell.stuttgart@kmee.com.br>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, osv
from openerp.tools.translate import _

from suds.client import Client, TransportError
from suds import WebFault


class WebServiceClient(object):

    def get_address(self, cr, uid, ids, context=None):

        for obj_model in self.browse(cr, uid, ids, context=context):

            if not obj_model.zip:
                return False

            zip_str = obj_model.zip.replace('-', '')

            if len(zip_str) == 8 and not self.pool.get('l10n_br.zip').search(
                    cr, uid, [('zip', '=', zip_str)]):

                # SigepWeb webservice url
                url_prod = 'https://apps.correios.com.br/SigepMasterJPA' \
                           '/AtendeClienteService/AtendeCliente?wsdl'

                try:

                    # Connect Brazil Correios webservice
                    res = Client(url_prod).service.consultaCEP(zip_str)

                    # Search state with state_code
                    state_ids = self.pool.get('res.country.state').search(
                        cr, uid, [('code', '=', str(res.uf))])

                    # city name
                    city_name = str(res.cidade.encode('utf8'))

                    # search city with name and state
                    city_ids = self.pool.get('l10n_br_base.city').search(
                        cr, uid, [('name', '=', city_name),
                                  ('state_id.id', 'in', state_ids)])

                    # Search Brazil id
                    country_ids = self.pool.get('res.country').search(
                        cr, uid, [('code', '=', 'BR')])

                    values = {
                        'zip': zip_str,
                        'street': str(res.end.encode('utf8')) if res.end else '',
                        'district': str(res.bairro.encode('utf8')) if res.bairro
                        else '',
                        'street_type': str(res.complemento.encode('utf8')) if res.complemento
                        else '',
                        'l10n_br_city_id': city_ids[0] if city_ids else False,
                        'state_id': state_ids[0] if state_ids else False,
                        'country_id': country_ids[0] if country_ids else False,
                    }

                    # Create zip object
                    self.pool.get('l10n_br.zip').create(cr, uid, values)

                except TransportError as e:
                    raise osv.except_osv(_('Error!'), _(e.message))
                except WebFault as e:
                    raise osv.except_osv(_('Error!'), _(e.message))

        return True
