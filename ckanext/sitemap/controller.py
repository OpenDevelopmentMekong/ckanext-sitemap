'''
Controller for sitemap
'''
import logging

from ckan.lib.base import BaseController
from ckan.model import Session, Package
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import url_for
from lxml import etree
from pylons import config, response
from pylons.decorators.cache import beaker_cache


SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

XHTML_NS = "http://www.w3.org/1999/xhtml"

log = logging.getLogger(__file__)

locales = config.get('ckan.locales_offered', '').split()


class SitemapController(BaseController):
    
    @staticmethod
    def domain_for_organization(orga_name):
        
        domain = "https://opendevelopmentmekong.net/"
        
        if orga_name == "cambodia-organization":
            domain = "https://opendevelopmentcambodia.net/"
        elif orga_name == "laos-organization":
            domain = "https://laos.opendevelopmentmekong.net/"
        elif orga_name == "vietnam-organization":
            domain = "https://vietnam.opendevelopmentmekong.net/"
        elif orga_name == "myanmar-organization":
            domain = "https://opendevelopmentmyanmar.net/"
        elif orga_name == "thailand-organization":
            domain = "https://thailand.opendevelopmentmyanmar.net/"
        
        return domain
        
    @staticmethod
    def _create_language_alternatives(domain, link, url):
        '''
        Create links (elements) for every language in locales_offered in .ini file
        :param link: string containing the link, eg. /dataset/xyz
        :param url: root node
        '''
        for lang in locales:
            attrib = {"rel": "alternate", "hreflang": lang, "href":
                      domain + lang + '/' + link}
            etree.SubElement(url, '{http://www.w3.org/1999/xhtml}link', attrib)

    @beaker_cache(expire=3600*24, type="dbm", invalidate_on_startup=True)
    def _render_sitemap(self):
        root = etree.Element("urlset", nsmap={None: SITEMAP_NS, 'xhtml': XHTML_NS})
        pkgs = Session.query(Package).filter(Package.private!=True).\
            filter(Package.state=='active').all()
            
        log.debug(pkgs)
        for pkg in pkgs:
            url = etree.SubElement(root, 'url')
            loc = etree.SubElement(url, 'loc')
            # pkg_url = url_for(controller='package', action="read", id=pkg.name)
            # loc.text = config.get('ckan.site_url') + pkg_url            
            result = toolkit.get_action('package_show')(data_dict={'id': pkg.name})
            organization = result['organization']
            domain = self.domain_for_organization(organization['name'])
            link = "dataset/?id=" + pkg.name
            loc.text = domain + link
            lastmod = etree.SubElement(url, 'lastmod')
            lastmod.text = pkg.latest_related_revision.timestamp.strftime('%Y-%m-%d')
            self._create_language_alternatives(domain, link, url)
            
        response.headers['Content-type'] = 'text/xml'
        return etree.tostring(root, pretty_print=True)
        
    def view(self):
        return self._render_sitemap()
