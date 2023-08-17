from scrapy.utils.sitemap import Sitemap


class TreeSitemap(Sitemap):
    # must change iter logic, to get the children of news tag
    # to be able to apply filter by upload_date or other metadata
    # TODO refactor
    def __iter__(self):
        for elem in self._root.getchildren():
            d = {}
            for el in elem.getchildren():
                tag = el.tag
                name = tag.split("}", 1)[1] if "}" in tag else tag
                d[name] = self._recursive(el)

            if "loc" in d:
                yield d

    def _recursive(self, root):
        d = {}
        tag = root.tag
        root_name = tag.split("}", 1)[1] if "}" in tag else tag
        if len(root):
            # if there are children
            for el in root.getchildren():
                tag = el.tag
                name = tag.split("}", 1)[1] if "}" in tag else tag
                
                value = self._recursive(el)
                d[name] = value

        else:
            # there is value, no children
            if root_name == "link":
                # if "href" in el.attrib:
                #     d.setdefault("alternate", []).append(root.get("href"))
                pass
            else:
                value = root.text.strip() if root.text else ""
        return d if d else value


# d = {
#     'loc': "https://www.n-tv.de/regionales/baden-wuerttemberg/Totes-Baby-in-Frauenhaus-Ermittlungen-eingestellt-article24289636.html",
#     'news': {
#         'publication': {
#             'name': "n-tv NACHRICHTEN",
#             'language': "de"
#         },
#         'title': "Baden-Württemberg: Totes Baby in Frauenhaus: Ermittlungen eingestellt"
#         ...
#     }
#     'image': {
#         'loc': ...
#     }

# }