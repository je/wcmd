from django import forms
from django.contrib import admin
#from django.contrib.gis.admin import OSMGeoAdmin
#from leaflet.admin import LeafletGeoAdmin
#from olwidget.admin import GeoModelAdmin
#from guardian.admin import GuardedModelAdmin
from wcmd.wcmd.models import *
from django.utils.translation import gettext_lazy as _

from django.forms.widgets import Textarea

from taggit.models import Tag
from import_export.admin import ImportExportModelAdmin
from import_export import fields, widgets
from import_export import resources

admin.site.site_header = 'WCMD administration'
admin.site_title = 'WCMD administration'
admin.site_url = 'wcmd/'
admin.index_title = 'WCMD administration'

class AgencyResource(resources.ModelResource):
    author_email = fields.Field(
        column_name='author_email',
        attribute='author',
        widget=widgets.ForeignKeyWidget(User, 'email'))

    class Meta:
        model = Agency
        use_natural_foreign_keys = True
        use_natural_primary_keys = True
        exclude = ('id','author')

class AgencyAdmin(ImportExportModelAdmin):
    list_display = ('sla', 'name', 'slug', 'author', 'created', 'modified',)
    ordering = ['name']
    list_per_page = 50
    search_fields = ('sla','name')
    date_hierarchy = 'created'
    list_display_links = ('sla', 'name',)
    readonly_fields = ['slug','author','modified','created']
    resource_class = AgencyResource

    fieldsets = (
      ('Identity', {'fields': ('sla', 'name', 'slug',), 'classes': ('show','extrapretty')}),
      ('Page', {'fields': ('page_content',), 'classes': ('show','extrapretty')}),
      ('More', {'fields': ('remarks',), 'classes': ('show',)}),
      ('Meta', {'fields': ('modified','created','author',), 'classes': ('show',)}),
    )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

admin.site.register(Agency, AgencyAdmin)

class WildernessResource(resources.ModelResource):
    author_email = fields.Field(
        column_name='author_email',
        attribute='author',
        widget=widgets.ForeignKeyWidget(User, 'email'))
    agency_sla = fields.Field(
        column_name='agency_sla',
        attribute='agency',
        widget=widgets.ForeignKeyWidget(Agency, 'sla'))
    tag_names = fields.Field(
        column_name='tag_names',
        attribute='tags',
        widget=widgets.ManyToManyWidget(Tag, field='name'))

    class Meta:
        model = Wilderness
        use_natural_foreign_keys = True
        use_natural_primary_keys = True
        exclude = ('id','author','agency','tags','geom')

class WildernessAdmin(ImportExportModelAdmin):
    list_display = ('name', 'get_sla', 'designation_date', 'author', 'created', 'modified',)
    ordering = ['name']
    list_per_page = 50
    search_fields = ('name',)
    date_hierarchy = 'designation_date'
    list_display_links = ('name',)
    list_filter = ('agency',)
    readonly_fields = ['slug','author','modified','created']
    resource_class = WildernessResource

    fieldsets = (
      ('Identity', {'fields': ('name', 'agency', 'slug',), 'classes': ('show','extrapretty')}),
      ('More', {'fields': ('designation_date','remarks',), 'classes': ('show',)}),
      ('Tags', {'fields': ('tags',)}),
      ('Page', {'fields': ('page_content',), 'classes': ('show','extrapretty')}),
      ('From Montana', {'fields': ('state','acreage','description','comment'), 'classes': ('show',)}),
      ('Geom', {'fields': ('geom',), 'classes': ('show',)}),
      ('Meta', {'fields': ('modified','created','author',), 'classes': ('show',)}),
    )

    @admin.display(ordering='agency__sla', description='agency')
    def get_sla(self, obj):
        return obj.agency.sla
    
    Agency.admin_order_field  = 'agency__sla'

    def get_queryset(self, request):
        return super(WildernessAdmin,self).get_queryset(request).select_related('agency')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

admin.site.register(Wilderness, WildernessAdmin)

class MeasureResource(resources.ModelResource):
    author_email = fields.Field(
        column_name='author_email',
        attribute='author',
        widget=widgets.ForeignKeyWidget(User, 'email'))
    agency_sla = fields.Field(
        column_name='agency_sla',
        attribute='agency',
        widget=widgets.ForeignKeyWidget(Agency, 'sla'))

    class Meta:
        model = Measure
        use_natural_foreign_keys = True
        use_natural_primary_keys = True
        exclude = ('id','author','agency', )

class MeasureAdmin(ImportExportModelAdmin):
    list_display = ('name', 'get_sla', 'required', 'reported_as', 'sortrank', 'author', 'created', 'modified',)
    ordering = ['agency','name']
    list_per_page = 50
    search_fields = ('name','fullname')
    #date_hierarchy = ''
    list_display_links = ('name',)
    list_filter = ('agency',)
    readonly_fields = ['slug','author','modified','created']
    resource_class = MeasureResource

    fieldsets = (
      ('Identity', {'fields': ('fullname', 'name', 'slug', 'indicator', 'question', 'quality', 'sortrank'), 'classes': ('show','extrapretty')}),
      ('More', {'fields': ('required', 'reported_as', 'units', 'formula', 'remarks',), 'classes': ('show',)}),
      ('Management', {'fields': ('agency',), 'classes': ('show',)}),
      ('Page', {'fields': ('page_content',), 'classes': ('show','extrapretty')}),
      ('Meta', {'fields': ('modified','created','author',), 'classes': ('show',)}),
    )

    @admin.display(ordering='agency__sla', description='agency')
    def get_sla(self, obj):
        return obj.agency.sla
    
    Agency.admin_order_field  = 'agency__sla'

    def get_queryset(self, request):
        return super(MeasureAdmin,self).get_queryset(request).select_related('agency')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

admin.site.register(Measure, MeasureAdmin)

class TrendReportResource(resources.ModelResource):
    author_email = fields.Field(
        column_name='author_email',
        attribute='author',
        widget=widgets.ForeignKeyWidget(User, 'email'))
    wilderness_name = fields.Field(
        column_name='wilderness_name',
        attribute='wilderness',
        widget=widgets.ForeignKeyWidget(Wilderness, 'name'))
    agency_sla = fields.Field(
        column_name='agency_sla',
        attribute='wilderness__agency',
        widget=widgets.ForeignKeyWidget(Agency, 'sla'))
    measure_names = fields.Field(
        column_name='measure_names',
        attribute='measures',
        widget=widgets.ManyToManyWidget(Measure, field='name'))

    class Meta:
        model = TrendReport
        use_natural_foreign_keys = True
        use_natural_primary_keys = True
        exclude = ('id','author','wilderness','measures' )

class TrendReportAdmin(ImportExportModelAdmin):
    list_display = ('name', 'wilderness', 'year', 'author', 'created', 'modified',)
    ordering = ['wilderness','year']
    list_per_page = 50
    search_fields = ('name',)
    #date_hierarchy = 'year'
    list_display_links = ('name',)
    list_filter = ('wilderness',)
    readonly_fields = ['author','modified','created']
    resource_class = TrendReportResource

    fieldsets = (
      ('Identity', {'fields': ('name',), 'classes': ('show','extrapretty')}),
      ('More', {'fields': ('wilderness', 'year',), 'classes': ('show',)}),
      ('Measures', {'fields': ('measures',), 'classes': ('show',)}),
      ('Meta', {'fields': ('direction', 'nextstep'), 'classes': ('show',)}),
      ('Page', {'fields': ('page_content',), 'classes': ('show','extrapretty')}),
      ('More', {'fields': ('remarks',), 'classes': ('show',)}),
      ('Meta', {'fields': ('modified','created','author',), 'classes': ('show',)}),
    )

    def get_queryset(self, request):
        return super(TrendReportAdmin,self).get_queryset(request).select_related('wilderness')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

admin.site.register(TrendReport, TrendReportAdmin)

class MeasureTrendResource(resources.ModelResource):
    author_email = fields.Field(
        column_name='author_email',
        attribute='author',
        widget=widgets.ForeignKeyWidget(User, 'email'))
    wilderness_name = fields.Field(
        column_name='wilderness_name',
        attribute='trendreport__wilderness',
        widget=widgets.ForeignKeyWidget(Wilderness, 'name'))
    agency_sla = fields.Field(
        column_name='agency_sla',
        attribute='trendreport__wilderness__agency',
        widget=widgets.ForeignKeyWidget(Agency, 'sla'))
    measure_name = fields.Field(
        column_name='measure_name',
        attribute='measure',
        widget=widgets.ForeignKeyWidget(Measure, 'name'))

    class Meta:
        model = MeasureTrend
        use_natural_foreign_keys = True
        use_natural_primary_keys = True
        exclude = ('id','author','trendreport','measure' )

class MeasureTrendAdmin(ImportExportModelAdmin):
    list_display = ('measure', 'year', 'direction', 'p_value', 'get_wilderness', 'get_reportyear', 'author', 'created', 'modified',)
    ordering = ['trendreport','year']
    list_per_page = 50
    #search_fields = ('name',)
    #date_hierarchy = 'year'
    list_display_links = ('measure',)
    list_filter = ('trendreport__wilderness', 'trendreport__year')
    readonly_fields = ['author','modified','created']
    resource_class = MeasureTrendResource

    fieldsets = (
      ('Identity', {'fields': ('measure', 'year'), 'classes': ('show','extrapretty')}),
      ('Report', {'fields': ('trendreport',), 'classes': ('show',)}),
      ('Trend', {'fields': ('direction', 'p_value', 'units', 'formula'), 'classes': ('show',)}),
      ('More', {'fields': ('remarks',), 'classes': ('show',)}),
      ('Meta', {'fields': ('modified','created','author',), 'classes': ('show',)}),
    )

    @admin.display(ordering='trendreport__wilderness', description='wilderness')
    def get_wilderness(self, obj):
        return obj.trendreport.wilderness
    
    Wilderness.admin_order_field  = 'trendreport__wilderness'

    @admin.display(ordering='trendreport__year', description='reportyear')
    def get_reportyear(self, obj):
        return obj.trendreport.year
    
    TrendReport.admin_order_field  = 'trendreport__year'

    def get_queryset(self, request):
        return super(MeasureTrendAdmin,self).get_queryset(request).select_related('trendreport')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(MeasureTrend, MeasureTrendAdmin)

class MeasureValueResource(resources.ModelResource):
    author_email = fields.Field(
        column_name='author_email',
        attribute='author',
        widget=widgets.ForeignKeyWidget(User, 'email'))
    wilderness_name = fields.Field(
        column_name='wilderness_name',
        attribute='measuretrend__trendreport__wilderness',
        widget=widgets.ForeignKeyWidget(Wilderness, 'name'))
    agency_sla = fields.Field(
        column_name='agency_sla',
        attribute='measuretrend__trendreport__wilderness__agency',
        widget=widgets.ForeignKeyWidget(Agency, 'sla'))
    measure_name = fields.Field(
        column_name='measure_name',
        attribute='measuretrend__measure',
        widget=widgets.ForeignKeyWidget(Measure, 'name'))

    class Meta:
        model = MeasureValue
        use_natural_foreign_keys = True
        use_natural_primary_keys = True
        exclude = ('id','author','measuretrend')

class MeasureValueAdmin(ImportExportModelAdmin):
    list_display = ('year', 'value', 'get_measuretrendyear', 'get_reportyear', 'get_wilderness', 'author', 'created', 'modified',)
    ordering = ['measuretrend__year','year']
    list_per_page = 50
    #search_fields = ('name',)
    #date_hierarchy = 'year'
    list_display_links = ('year',)
    list_filter = ('measuretrend__trendreport__wilderness', 'measuretrend__trendreport__year')
    readonly_fields = ['author','modified','created']
    resource_class = MeasureValueResource

    fieldsets = (
      #('Identity', {'fields': ('measuretrend__year', 'measuretrend__trendreport__year'), 'classes': ('show','extrapretty')}),
      ('Report', {'fields': ('measuretrend',), 'classes': ('show',)}),
      ('Value', {'fields': ('cat', 'year', 'value',), 'classes': ('show',)}),
      ('More', {'fields': ('remarks',), 'classes': ('show',)}),
      ('Meta', {'fields': ('modified','created','author',), 'classes': ('show',)}),
    )

    @admin.display(ordering='measuretrend__trendreport__wilderness', description='wilderness')
    def get_wilderness(self, obj):
        return obj.measuretrend.trendreport.wilderness
    
    Wilderness.admin_order_field  = 'measuretrend__trendreport__wilderness'

    @admin.display(ordering='measuretrend__trendreport__year', description='reportyear')
    def get_reportyear(self, obj):
        return obj.measuretrend.trendreport.year
    
    TrendReport.admin_order_field  = 'measuretrend__trendreport__year'

    @admin.display(ordering='measuretrend__year', description='measuretrendyear')
    def get_measuretrendyear(self, obj):
        return obj.measuretrend.trendreport.year
    
    MeasureTrend.admin_order_field  = 'measuretrend__year'

    def get_queryset(self, request):
        return super(MeasureValueAdmin,self).get_queryset(request).select_related('measuretrend')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(MeasureValue, MeasureValueAdmin)
