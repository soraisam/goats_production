from django import forms
from django.forms.widgets import Textarea
from django.templatetags.static import static
from tom_antares.antares import ANTARESBrokerForm, ANTARESBroker
import marshmallow
import antares_client


class GOATSANTARESBrokerForm(ANTARESBrokerForm):
    """A Django form class that extends ``ANTARESBrokerForm``.

    Attributes
    ----------
    esquery : `JSONField`
        A JSON field, required for receiving Elastic Search queries.
    """

    esquery = forms.JSONField(
        required=False,
        label="Elastic Search query in JSON format",
        widget=Textarea(attrs={
            "rows": 10,
            "id": "esquery"
        }),
        initial=None
    )

    class Media:
        js = (static("js/esquery.js"), )


class GOATSANTARESBroker(ANTARESBroker):
    """Extends ``ANTARESBroker`` to use GOATS Broker form."""

    form = GOATSANTARESBrokerForm

    def fetch_alerts(self, parameters: dict) -> iter:
        tags = parameters.get('tag')
        nobs_gt = parameters.get('nobs__gt')
        nobs_lt = parameters.get('nobs__lt')
        sra = parameters.get('ra')
        sdec = parameters.get('dec')
        ssr = parameters.get('sr')
        mjd_gt = parameters.get('mjd__gt')
        mjd_lt = parameters.get('mjd__lt')
        mag_min = parameters.get('mag__min')
        mag_max = parameters.get('mag__max')
        elsquery = parameters.get('esquery')
        ztfid = parameters.get('ztfid')
        max_alerts = parameters.get('max_alerts', 20)
        locusid = parameters.get('locusid')
        if ztfid:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "properties.ztf_object_id": ztfid
                                }
                            }
                        ]
                    }
                }
            }
        elif locusid:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "locus_id": locusid
                                }
                            }
                        ]
                    }
                }
            }
        elif elsquery:
            query = elsquery
        else:
            filters = []

            if nobs_gt or nobs_lt:
                nobs_range = {'range': {'properties.num_mag_values': {}}}
                if nobs_gt:
                    nobs_range['range']['properties.num_mag_values']['gte'] = nobs_gt
                if nobs_lt:
                    nobs_range['range']['properties.num_mag_values']['lte'] = nobs_lt
                filters.append(nobs_range)

            if mjd_lt:
                mjd_lt_range = {'range': {'properties.newest_alert_observation_time': {'lte': mjd_lt}}}
                filters.append(mjd_lt_range)

            if mjd_gt:
                mjd_gt_range = {'range': {'properties.oldest_alert_observation_time': {'gte': mjd_gt}}}
                filters.append(mjd_gt_range)

            if mag_min or mag_max:
                mag_range = {'range': {'properties.newest_alert_magnitude': {}}}
                if mag_min:
                    mag_range['range']['properties.newest_alert_magnitude']['gte'] = mag_min
                if mag_max:
                    mag_range['range']['properties.newest_alert_magnitude']['lte'] = mag_max
                filters.append(mag_range)

            if sra and ssr:  # TODO: add cross-field validation
                ra_range = {'range': {'ra': {'gte': sra-ssr, 'lte': sra+ssr}}}
                filters.append(ra_range)

            if sdec and ssr:  # TODO: add cross-field validation
                dec_range = {'range': {'dec': {'gte': sdec-ssr, 'lte': sdec+ssr}}}
                filters.append(dec_range)

            if tags:
                filters.append({'terms': {'tags': tags}})

            query = {
                "query": {
                    "bool": {
                        "filter": filters
                    }
                }
            }

        loci = antares_client.search.search(query)
#        if ztfid:
#            loci = get_by_ztf_object_id(ztfid)
        alerts = []
        while len(alerts) < max_alerts:
            try:
                locus = next(loci)
            except (marshmallow.exceptions.ValidationError, StopIteration):
                break
            alerts.append(self.alert_to_dict(locus))
        return iter(alerts)
