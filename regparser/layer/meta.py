import re

from layer import Layer
import settings


class Meta(Layer):
    def process(self, node):
        """If this is the root element, add some 'meta' information about
        this regulation, including its cfr title, effective date, and any
        configured info"""
        if len(node.label) != 1:
            return

        layer = {
            'cfr_title_number': self.cfr_title,
            'cfr_title_text': settings.CFR_TITLES[self.cfr_title]
        }

        if node.title:
            # up till the paren
            match = re.search('part \d+[^\w]*([^\(]*)', node.title, re.I)
            if match:
                layer['statutory_name'] = match.group(1).strip()
            match = re.search('\(regulation (\w+)\)', node.title, re.I)
            if match:
                layer['reg_letter'] = match.group(1)

        effective_date = self.effective_date()
        if effective_date:
            layer['effective_date'] = effective_date

        return [dict(layer.items() + settings.META.items())]

    def effective_date(self):
        if self.version:
            return self.version.effective.isoformat()
        last_notice = filter(lambda n: n['document_number'] == self.version_id,
                             self.notices)
        if last_notice and 'effective_on' in last_notice[0]:
            return last_notice[0]['effective_on']
