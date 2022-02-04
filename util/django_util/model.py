from django.db.models import Count


def getUniqueField(query, field):
    """count and group by field"""
    mdlabels = query.values(field).annotate(count=Count(field)).order_by('-count')
    labels = []
    sumLabel = 0
    for md in mdlabels:
        sumLabel += md['count']
        labels.append(md)
    labels.insert(0, {'count': sumLabel, field: 'all'})
    return labels
