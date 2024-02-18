from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Min, Max, Q
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from taggit.models import Tag


from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory

from itertools import groupby
from wcmd.wcmd.models import *
from wcmd.wcmd.forms import *
import json

def user_landing(request):
    user = get_object_or_404(User, username=request.user.username)
    return render(request, 'wcmd/user_detail.html', {'user' : user})

def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'wcmd/user_detail.html', {'user' : user})

class UserList(ListView):
    model = User
    queryset = User.objects.all()#.annotate(wilderness_count=Count('wilderness_agency'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def sortedZipLongest(l1, l2, key1, key2, fillvalue={}):  
    l1 = iter(sorted(l1, key=lambda x: x[key1]))
    l2 = iter(sorted(l2, key=lambda x: x[key2]))
    u = next(l1, None)
    v = next(l2, None)

    while (u is not None) or (v is not None):  
        if u is None:
            yield fillvalue, v
            v = next(l2, None)
        elif v is None:
            yield u, fillvalue
            u = next(l1, None)
        elif u.get(key1) == v.get(key2):
            yield u, v
            u = next(l1, None)
            v = next(l2, None)
        elif u.get(key1) < v.get(key2):
            yield u, fillvalue
            u = next(l1, None)
        else:
            yield fillvalue, v
            v = next(l2, None)

class AgencyList(ListView):
    model = Agency
    queryset = Agency.objects.all().defer("page_content","remarks").annotate(wilderness_count=Count('wilderness_agency'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AgencyDetail(DetailView):
    model = Agency

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['w_list'] = Wilderness.objects.filter(agency=self.get_object()).defer("geom","page_content","description","comment","remarks")#.annotate(tr_count=Count('trendreport_wilderness'))#.order_by('name')
        context['tr_count'] = Wilderness.objects.filter(agency=self.get_object()).defer("geom","page_content","description","comment","remarks").aggregate(Count('trendreport_wilderness'))['trendreport_wilderness__count']
        context['tag_list'] = Tag.objects.filter(wilderness__in=context['w_list']).distinct().order_by("name")

        m_list = Measure.objects.filter(agency=self.get_object()).defer("page_content","remarks")
        context['m_list'] = m_list

        ma = m_list.values('pk', 'name', 'required', 'slug', 'indicator', 'question', 'quality')
        lmat = list(ma)
        #lmat = [{**u, **v} for u, v in sortedZipLongest(lma, ltrm, key1="pk", key2="measure", fillvalue={})]

        gi = []
        for k,v in groupby(lmat,key=lambda x:x['indicator']):
            gi.append({'name':k,'trend': ''})
        gqi = []
        for k,v in groupby(lmat,key=lambda x:[x['question'], x['indicator']]):
            gqi.append({'qi':k,'trend': ''})
        gq = []
        for k,v in groupby(gqi,key=lambda x:x['qi'][0]):
            gq.append({'name':k,'trend': ''})
        gqqi = []
        for k,v in groupby(lmat,key=lambda x:[x['quality'], x['question'], x['indicator']]):
            gqqi.append({'qqi':k,'trend': ''})
        gqq = []
        for k,v in groupby(gqqi,key=lambda x:x['qqi'][0]):
            gqq.append({'name':k,'trend': ''})

        for indi in gi:
            indi['children'] = [d for d in lmat if d['indicator'] == indi['name']]
        for quest in gq:
            indicators = [i['qqi'] for i in gqqi]
            i_list = [i[2] for i in indicators if i[1] == quest['name']]        
            quest['children'] = [d for d in gi if d['name'] in i_list]
        for qual in gqq:
            indicators = [i['qqi'] for i in gqqi]
            q_list = [i[1] for i in indicators if i[0] == qual['name']]
            qual['children'] = [d for d in gq if d['name'] in q_list]

        ajson = json.dumps(gqq)
        sjson = '{"name": "Character", "children": ' + ajson + '}'
        context['mjson'] = json.loads(sjson)

        context['tw'] = sorted(filter(None, list(Wilderness.objects.filter(agency=self.get_object()).defer("geom","page_content","description","comment","remarks").order_by().values_list('trendreport_wilderness__year', flat=True).distinct())))
        return context

def agency_measures_edit(request, aslug):
    pass

class AgencyMeasureInline(InlineFormSetFactory):
    model = Measure
    form_class = AgencyMeasureForm
    #fields = ['name', 'fullname', 'slug', 'sortrank', 'indicator', 'question', 'quality', 'remarks', 'required', 'page_content', 'reported_as', 'formula', 'units']
    factory_kwargs = {"extra": 1}

class CreateAgencyView(CreateWithInlinesView):
    model = Agency
    form_class = AgencyForm
    inlines = [AgencyMeasureInline]
    #fields = ['name', 'slug', 'sla', 'page_content', 'remarks']
    template_name = 'wcmd/agency_edit.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

class AgencyEditView(PermissionRequiredMixin, UpdateWithInlinesView):
    permission_required = ('wcmd.view_agency', 'wcmd.change_agency')
    model = Agency
    form_class = AgencyForm
    #inlines = [AgencyMeasureInline]
    #fields = ['name', 'slug', 'sla', 'page_content', 'remarks']
    template_name = 'wcmd/agency_edit.html'
    #success_url = self.object.get_absolute_url()

    def get_success_url(self):
        return self.object.get_absolute_url()

class AgencyMeasuresEditView(PermissionRequiredMixin, UpdateWithInlinesView):
    permission_required = ('wcmd.view_agency', 'wcmd.change_agency')
    model = Agency
    form_class = AgencyMeasuresForm
    inlines = [AgencyMeasureInline]
    #fields = ['name', 'slug', 'sla', 'page_content', 'remarks']
    template_name = 'wcmd/agency_edit.html'
    #success_url = self.object.get_absolute_url()

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.agency = self.get_agency()
        return super().form_valid(form)

class AgencyMeasureAddView(CreateWithInlinesView):
    model = Measure
    form_class = AgencyMeasureForm
    #inlines = [AgencyMeasureInline]
    #fields = ['agency', 'fullname', 'name', 'sortrank', 'indicator', 'question', 'quality', 'required', 'reported_as', 'units', 'formula', 'page_content', 'remarks']
    template_name = 'wcmd/measure_edit.html'

    def get_agency(self):
        return get_object_or_404(Agency,
            slug=self.kwargs['aslug'],
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.agency = self.get_agency()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

class AgencyMeasureEditView(PermissionRequiredMixin, UpdateWithInlinesView):
    permission_required = ('wcmd.view_agency', 'wcmd.change_agency')
    model = Measure
    form_class = AgencyMeasureForm
    #inlines = [AgencyMeasureInline]
    #fields = ['name', 'slug', 'sla', 'page_content', 'remarks']
    template_name = 'wcmd/measure_edit.html'
    #success_url = self.object.get_absolute_url()

    def get_agency(self):
        return get_object_or_404(Agency,
            slug=self.kwargs['aslug'],
        )

    def form_valid(self, form):
        form.instance.agency = self.get_agency()
        return super().form_valid(form)

    def get_object(self):
        return get_object_or_404(Measure,
            agency__slug=self.kwargs['aslug'],
            slug=self.kwargs['mslug']
        )

    def get_success_url(self):
        return self.object.get_absolute_url()

def agency_measure_detail(request, aslug, mslug):
    m = Measure.objects.defer("page_content","remarks").get(agency__slug__iexact=aslug, slug__iexact=mslug)
    trs_list = TrendReport.objects.filter(wilderness__agency__slug__iexact=aslug, measures__slug__iexact=mslug).defer("page_content","remarks")
    trv_list = TrendReport.objects.filter(wilderness__agency__slug__iexact=aslug, measuretrend_trendreport__measure__slug__iexact=mslug).defer("page_content","remarks").prefetch_related('measuretrend_trendreport')
    tr_list = trs_list.union(trv_list)
    tw = []
    for tr in tr_list:
        selected = tr.measures.values_list('slug', flat=True)
        reported = tr.measuretrend_trendreport.values_list('measure__slug', flat=True)
        measures_all = [m.slug]
        #ma = Measure.objects.filter(slug__in=measures_all).values('pk', 'name', 'slug')
        ma = Measure.objects.filter(Q(slug__in=measures_all)&Q(agency__slug=aslug)).values('pk', 'name', 'slug')
        for m_ in ma:
            if m_['slug'] in selected:
                m_['selected'] = 'yes'
        trm = tr.measuretrend_trendreport.filter(measure__slug__in=measures_all).values('measure','year','direction')
        lma = list(ma)
        ltrm = list(trm)
        tr.lmat = [{**u, **v} for u, v in sortedZipLongest(lma, ltrm, key1="pk", key2="measure", fillvalue={})][0]
        tw.append(tr.year)
    m.tw = sorted(list(set(tw)))

    g = [{"name":m.name, "required": m.required}]
    gi = []
    gi.append({"name":m.indicator, "children": g})
    gq = []
    gq.append({"name":m.question, "children": gi})
    gqq = []
    gqq.append({"name":m.quality, "children": gq})

    ajson = json.dumps(gqq)
    sjson = '{"name": "Character", "children": ' + ajson + '}'
    mjson = json.loads(sjson)

    return render(request,'wcmd/agency_measure_detail.html', {
        'object': m, 'tr_list': tr_list, 'trs_list': trs_list,'trv_list': trv_list, 'mjson': mjson
    })

def wilderness_detail(request, aslug, wslug):
    w = Wilderness.objects.defer("geom","remarks").get(agency__slug__iexact=aslug, slug__iexact=wslug)

    #tr_list = w.trendreport_set.all() # why no?
    tr_list = TrendReport.objects.filter(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug).defer("page_content","remarks")
    lmat = []
    slmat = []
    wltrm = 0
    for tr in tr_list:
        selected = tr.measures.values_list('slug', flat=True)
        reported = tr.measuretrend_trendreport.values_list('measure__slug', flat=True)
        measures_all = selected.union(reported)
        lmat = lmat + list(measures_all)
        #ma = Measure.objects.filter(slug__in=measures_all).values('pk', 'sortrank', 'name', 'slug')
        ma = Measure.objects.filter(Q(slug__in=measures_all)&Q(agency__slug=aslug)).values('pk', 'sortrank', 'name', 'slug')
        for m in ma:
            if m['slug'] in selected:
                m['selected'] = 'yes'
        trm = tr.measuretrend_trendreport.filter(measure__slug__in=measures_all).values('measure','year','direction')
        lma = list(ma)
        ltrm = list(trm)
        wltrm = wltrm + len(ltrm)
        tr.lmat = [{**u, **v} for u, v in sortedZipLongest(lma, ltrm, key1="pk", key2="measure", fillvalue={})]
        tr.slmat = [{k: v for k, v in d.items() if k in ['sortrank','slug','name']} for d in tr.lmat]
        slmat = slmat + tr.slmat
    w.wltrm = wltrm
    w_slmatx = [dict(s) for s in set(frozenset(d.items()) for d in slmat)]
    w_m_list = sorted(w_slmatx, key=lambda d: d['sortrank'])
    #w_m_list = list(dict.fromkeys([ item['slug'] for item in w_slmat ]))

    return render(request,'wcmd/wilderness_detail.html', {
        'object': w, 'tr_list': tr_list,'w_m_list': w_m_list,
    })

def wilderness_measures_edit(request, aslug, wslug):
    pass

class WildernessEditView(PermissionRequiredMixin, UpdateWithInlinesView):
    permission_required = ('wcmd.view_agency', 'wcmd.change_agency')
    model = Wilderness
    form_class = WildernessForm
    #inlines = [WildernessMeasureInline]
    #fields = ['name', 'slug', 'sla', 'page_content', 'remarks']
    template_name = 'wcmd/wilderness_edit.html'
    #success_url = self.object.get_absolute_url()

    def get_object(self):
        return get_object_or_404(Wilderness,
            agency__slug=self.kwargs['aslug'],
            slug=self.kwargs['wslug']
        )

    def get_success_url(self):
        return self.object.get_absolute_url()

def wilderness_measure_detail(request, aslug, wslug, mslug):
    w = Wilderness.objects.defer("geom","page_content","description","comment","remarks").get(agency__slug__iexact=aslug, slug__iexact=wslug)
    m = Measure.objects.get(agency__slug__iexact=aslug, slug__iexact=mslug)
    trs_list = TrendReport.objects.filter(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug, measures__slug__iexact=mslug).defer("page_content","remarks") # selected
    trv_list = TrendReport.objects.filter(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug, measuretrend_trendreport__measure__slug__iexact=mslug).defer("page_content","remarks").prefetch_related('measuretrend_trendreport')
    tr_list = trs_list.union(trv_list)
    tw = []
    for tr in tr_list:
        selected = tr.measures.values_list('slug', flat=True)
        reported = tr.measuretrend_trendreport.values_list('measure__slug', flat=True)
        measures_all = [m.slug]
        ma = Measure.objects.filter(slug__in=measures_all).values('pk', 'name', 'slug')
        for m_ in ma:
            if m_['slug'] in selected:
                m_['selected'] = 'yes'
        trm = tr.measuretrend_trendreport.filter(measure__slug__in=measures_all).values('measure','year','direction')
        lma = list(ma)
        ltrm = list(trm)
        tr.lmat = [{**u, **v} for u, v in sortedZipLongest(lma, ltrm, key1="pk", key2="measure", fillvalue={})][0]
        tw.append(tr.year)
    m.tw = sorted(list(set(tw)))

    g = [{"name":m.name, "required": m.required}]
    gi = []
    gi.append({"name":m.indicator, "children": g})
    gq = []
    gq.append({"name":m.question, "children": gi})
    gqq = []
    gqq.append({"name":m.quality, "children": gq})

    ajson = json.dumps(gqq)
    sjson = '{"name": "Character", "children": ' + ajson + '}'
    mjson = json.loads(sjson)

    return render(request,'wcmd/wilderness_measure_detail.html', {
        'object': w, 'm': m, 'tr_list': tr_list, 'trs_list': trs_list,'trv_list': trv_list, 'mjson': mjson
    })

def trendreport_edit(request, aslug, wslug, year):
    pass

def trendreport_detail(request, aslug, wslug, year):
    tr = TrendReport.objects.get(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug, year=year)
    measures = tr.measures.values_list('slug', flat=True)
    trend_measures = tr.measuretrend_trendreport.values_list('measure__slug', flat=True)
    measures_all = measures.union(trend_measures)
    #ma = Measure.objects.filter(Q(slug__in=measures_all)&Q(agency__slug=aslug)).values('pk', 'name', 'required', 'slug', 'indicator', 'question', 'quality')
    ma = Measure.objects.filter(agency__slug=aslug).values('pk', 'name', 'required', 'slug', 'indicator', 'question', 'quality')
    trm = tr.measuretrend_trendreport.filter(measure__slug__in=measures_all).values('measure','year','direction')
    lma = list(ma)
    ltrm = list(trm)
    lmat = [{**u, **v} for u, v in sortedZipLongest(lma, ltrm, key1="pk", key2="measure", fillvalue={})]
    for d in lmat:
        if d['slug'] in measures:
            d['selected'] = 'yes'
        else:
            d['selected'] = ''
        if 'direction' in d:
            d['trend'] = d['direction']
            if d['direction'] == 'I':
                d['trend'] = 1
            elif d['direction'] == 'S':
                d['trend'] = 0
            elif d['direction'] == 'O':
                d['trend'] = 0
            elif d['direction'] == 'D':
                d['trend'] = -1
        else:
            d['trend'] = ''

    gi = []
    for k,v in groupby(lmat,key=lambda x:x['indicator']):
        v2 = [d for d in v if d['trend'] is not '']
        if v2:
            ds = sum(int(d['trend']) for d in v2)
            gi.append({'name':k,'trend':1 if ds > 0 else -1 if ds < 0 else 0 if ds == 0 else ''})
        else:
            gi.append({'name':k,'trend': ''})
    gqi = []
    for k,v in groupby(lmat,key=lambda x:[x['question'], x['indicator']]):
        v2 = [d for d in v if d['trend'] is not '']
        if v2:
            ds = sum(int(d['trend']) for d in v2)
            gqi.append({'qi':k,'trend':1 if ds > 0 else -1 if ds < 0 else 0 if ds == 0 else ''})
        else:
            gqi.append({'qi':k,'trend': ''})
    gq = []
    for k,v in groupby(gqi,key=lambda x:x['qi'][0]):
        v2 = [d for d in v if d['trend'] is not '']
        if v2:
            ds = sum(int(d['trend']) for d in v2)
            gq.append({'name':k,'trend':1 if ds > 0 else -1 if ds < 0 else 0 if ds == 0 else ''})
        else:
            gq.append({'name':k,'trend': ''})

    gqqi = []
    for k,v in groupby(lmat,key=lambda x:[x['quality'], x['question'], x['indicator']]):
        v2 = [d for d in v if d['trend'] is not '']
        if v2:
            ds = sum(int(d['trend']) for d in v2)
            gqqi.append({'qqi':k,'trend':1 if ds > 0 else -1 if ds < 0 else 0 if ds == 0 else ''})
        else:
            gqqi.append({'qqi':k,'trend': ''})
    gqq = []
    for k,v in groupby(gqqi,key=lambda x:x['qqi'][0]):
        v2 = [d for d in v if d['trend'] is not '']
        if v2:
            ds = sum(int(d['trend']) for d in v2)
            gqq.append({'name':k,'trend':1 if ds > 0 else -1 if ds < 0 else 0 if ds == 0 else ''})
        else:
            gqq.append({'name':k,'trend': ''})

    for indi in gi:
        indi['children'] = [d for d in lmat if d['indicator'] == indi['name']]
        indi['selected'] = ''
        if len([d for d in indi['children'] if d['selected'] == 'yes']) > 0:
            indi['selected'] = 'yes'
    for quest in gq:
        indicators = [i['qqi'] for i in gqqi]
        i_list = [i[2] for i in indicators if i[1] == quest['name']]        
        quest['children'] = [d for d in gi if d['name'] in i_list]
        quest['selected'] = ''
        if len([d for d in quest['children'] if d['selected'] == 'yes']) > 0:
            quest['selected'] = 'yes'
    for qual in gqq:
        indicators = [i['qqi'] for i in gqqi]
        q_list = [i[1] for i in indicators if i[0] == qual['name']]
        qual['children'] = [d for d in gq if d['name'] in q_list]
        qual['selected'] = ''
        if len([d for d in qual['children'] if d['selected'] == 'yes']) > 0:
            qual['selected'] = 'yes'

    ajson = json.dumps(gqq)
    sjson = '{"name": "Character", "children": ' + ajson + '}'
    mjson = json.loads(sjson)

    qtt = [d['trend'] for d in gqq if d['trend'] is not '']
    qt = [sum(qtt)]
    qt.append(sum(1 for x in qtt if x < 0))
    qt.append(sum(1 for x in qtt if x == 0))
    qt.append(sum(1 for x in qtt if x > 0))
    qt.append(len(measures_all))

    return render(request,'wcmd/trendreport_detail.html', {
        'object': tr, 'ma': ma, 'measures_all': measures_all, 'measures': measures, 'trend_measures': trend_measures, 'trm': trm, 'lmat': lmat, 'gi': gi, 'gq': gq, 'gqq': gqq, 'gqi': gqi, 'gqqi': gqqi, 'mjson': mjson, 'qtt': qtt, 'qt': qt
    })

def trendreport_measure_edit(request, aslug, wslug, year, mslug):
    pass

def trendreport_measure_detail(request, aslug, wslug, year, mslug):
    w = Wilderness.objects.defer("geom","page_content").get(agency__slug__iexact=aslug, slug__iexact=wslug)
    m = Measure.objects.defer("page_content","remarks").get(agency__slug__iexact=aslug, slug__iexact=mslug)
    tr = TrendReport.objects.prefetch_related('measuretrend_trendreport').defer("page_content","remarks").get(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug, year=year)

    #trs_list = TrendReport.objects.filter(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug, year=year, measures__slug__iexact=mslug) # selected
    #trv_list = TrendReport.objects.prefetch_related('measuretrend_trendreport').filter(wilderness__agency__slug__iexact=aslug, wilderness__slug__iexact=wslug, year=year, measuretrend_trendreport__measure__slug__iexact=mslug)
    #tr_list = trs_list.union(trv_list)

    selected = tr.measures.values_list('slug', flat=True)
    reported = tr.measuretrend_trendreport.values_list('measure__slug', flat=True)
    measures_all = [m.slug]
    #ma = Measure.objects.filter(slug__in=measures_all).values('pk', 'name', 'slug')
    ma = Measure.objects.filter(agency__slug=aslug).values('pk', 'name', 'slug')
    for d in ma:
        if d['slug'] in selected:
            d['selected'] = 'yes'
        if 'direction' in d:
            d['trend'] = d['direction']
            if d['direction'] == 'I':
                d['trend'] = 1
            elif d['direction'] == 'S':
                d['trend'] = 0
            elif d['direction'] == 'O':
                d['trend'] = 0
            elif d['direction'] == 'D':
                d['trend'] = -1
        else:
            d['trend'] = ''

    trm = tr.measuretrend_trendreport.filter(measure__slug__in=measures_all).values('measure','year','direction')
    lma = list(ma)
    ltrm = list(trm)
    tr.lmat = [{**u, **v} for u, v in sortedZipLongest(lma, ltrm, key1="pk", key2="measure", fillvalue={})][0]

    g = [{"name":m.name, "required": m.required}]
    gi = []
    gi.append({"name":m.indicator, "children": g})
    gq = []
    gq.append({"name":m.question, "children": gi})
    gqq = []
    gqq.append({"name":m.quality, "children": gq})

    ajson = json.dumps(gqq)
    sjson = '{"name": "Character", "children": ' + ajson + '}'
    mjson = json.loads(sjson)

    return render(request,'wcmd/trendreport_measure_detail.html', {
        'w': w, 'object': tr, 'm': m, 'mjson': mjson
    })

class WildernessDetail(DetailView):
    model = Wilderness

    def get_context_data(self, **kwargs):
        context = super(WildernessDetail, self).get_context_data(**kwargs)
        #context['ups'] = EventFile.objects.filter(event=self.get_object())
        #context['links'] = EventLink.objects.filter(event=self.get_object())
        # model = Model.objects.get(name=self.kwargs['name'])
        # context['model'] = model
        # context['muser_list'] = get_users_with_perms(context['model'])
        #context['event'] = Event.objects.get(id=self.kwargs['pk'])
        # context['user_list'] = get_users_with_perms(context['entity'])
        # context['field_list'] = Field.objects.filter(model__name=self.kwargs['name'])
        #distance = 16093 # 10 mi
        #distance = 1609 # 1 mi
        #es = Entity.objects.filter(model__name=self.kwargs['name'])
        #for each in Entity.objects.filter(model__name=self.kwargs['name']):
        #    each.simple = each.geom.convex_hull
        #    each.save()
        #ref_location = Event.objects.get(id=self.kwargs['pk']).geom
        #context['ref_location'] = ref_location
        #context['nearby'] = Event.objects.exclude(id=self.kwargs['pk']).filter(ok=True).filter(geom__distance_lte=(ref_location, D(m=distance))).distance(ref_location).order_by('distance')[:10]
        #related_models = Model.objects.filter(id__in=model.related_models.all())
        #related_models = Posts.objects.filter(user__userprofile__in=UserProfile.objects.get(user=your_user_object).following.all())
        #for m in related_models:
        ### context['fires'] = Fire.objects.filter(geom__distance_lte=(ref_location, D(m=distance))).distance(ref_location).order_by('distance')
        #context['related_models'] = related_models
        return context
