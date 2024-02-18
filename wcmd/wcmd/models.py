from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Manager as GeoManager
from django.contrib.gis.db.models import GeometryField
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.utils.timezone import now
from taggit.managers import TaggableManager

import datetime
import uuid

class AgencyManager(models.Manager):
    def get_by_natural_key(self, sla):
        return self.get(sla=sla)

class Agency(models.Model): # an agency
    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="agency_author")
    name = models.CharField('Name', unique=True, max_length=40, help_text="")
    slug = models.CharField('Slug', unique=True, max_length=40, help_text="No spaces.")
    sla = models.CharField('SLA', unique=True, max_length=6, help_text="")
    page_content = models.TextField(_("content"), blank=True)
    remarks = models.TextField('Remarks', max_length=1024, blank=True, null=True, help_text="", )
    objects = AgencyManager()

    # related: wilderness list

    class Meta:
        verbose_name = _('agency')
        verbose_name_plural = _('agencies')
        ordering = ['name',]

    def __str__(self):
        return '%s' % (self.name)

    def get_absolute_url(self):
        return "/wcmd/%s/" % (self.slug)

    def natural_key(self):
        return (self.sla)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Agency, self).save(*args, **kwargs)

class WildernessManager(GeoManager):
    def get_by_natural_key(self, agency, name):
        return self.get(agency=agency, name=name)

class Wilderness(models.Model): # a wilderness, which can have more than one agency managing
    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="wilderness_author")
    name = models.CharField('Name', max_length=80, help_text="")
    slug = models.CharField('Slug', max_length=80, help_text="No spaces.")
    designation_date = models.DateField('Date Designated', help_text="")
    #delist_date = models.DateField('Date Delisted', blank=True, null=True, help_text="")
    remarks = models.TextField('Remarks', max_length=1024, blank=True, null=True, help_text="", )
    page_content = models.TextField(_("content"), blank=True)
    state = models.CharField('State', max_length=14, blank=True, null=True, help_text="From Montana", )
    comment = models.TextField('Comment', max_length=1024, blank=True, null=True, help_text="From Montana", )
    acreage = models.PositiveIntegerField('Acreage', blank=True, null=True, help_text="From Montana", )
    description = models.TextField('Description', max_length=1024, blank=True, null=True, help_text="From Montana", )
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name="wilderness_agency")
    tags = TaggableManager(blank=True)
    geom = GeometryField(blank=True, null=True, )
    objects = WildernessManager()

    # version by year maybe in query agency + name join date_listed

    # related: trendreport list

    class Meta:
        verbose_name = _('wilderness area')
        verbose_name_plural = _('wilderness areas')
        unique_together = [['name', 'agency',], ['slug', 'agency',]]
        ordering = ['name','agency']

    def __str__(self):
        return '%s' % (self.name)

    def get_absolute_url(self):
        return "/wcmd/%s/%s/" % (self.agency.slug, self.slug)

    def natural_key(self):
        return (self.name, self.agency)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Wilderness, self).save(*args, **kwargs)

class MeasureManager(models.Manager):
    def get_by_natural_key(self, agency, name):
        return self.get(agency=agency, name=name)

class Measure(models.Model): # a measure, which is a formula and not a trend or list of values

    class ReportedAs(models.TextChoices):
        SINGLE_VALUE = 'VAL', _('Single value for report year')
        CAT_VALUES = 'CAT', _('Value for each category in a set')
        SERIES_OF_VALUES = 'COL', _('Series of annual values')
        TREND_DIR = 'TRD', _('Trend direction and significance')

    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="measure_author")
    fullname = models.CharField('Name', max_length=800, help_text="")
    name = models.CharField('Abridged Name', max_length=80, help_text="")
    slug = models.CharField('Slug', max_length=80, help_text="No spaces.")
    sortrank = models.PositiveSmallIntegerField('SortRank', blank=True, null=True, help_text="")
    indicator = models.CharField('Indicator', max_length=80, blank=True, null=True, help_text="")
    question = models.CharField('Question', max_length=80, blank=True, null=True, help_text="")
    quality = models.CharField('Quality', max_length=80, blank=True, null=True, help_text="")
    remarks = models.TextField('Remarks', max_length=1024, blank=True, null=True, help_text="", )
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, blank=True, related_name="measure_agency")
    required = models.CharField('Required', max_length=80, help_text="'YES','OPTIONAL', or 'ONE_OR_MORE_NN' where NN is the RTSALO group ID")
    page_content = models.TextField(_("content"), blank=True)
    reported_as = models.CharField(
        'Reported As',
        max_length=3,
        choices=ReportedAs.choices
    )
    formula = models.TextField('Formula', max_length=1024, blank=True, null=True, help_text="", )# how to calc trend from designation year, trend year, and selected measure values
    units = models.CharField('Units', max_length=80, blank=True, null=True, help_text="")
    objects = MeasureManager()

    class Meta:
        verbose_name = _('measure')
        verbose_name_plural = _('measures')
        unique_together = [['name', 'agency'], ['fullname', 'agency'], ['slug', 'agency']]
        ordering = ['sortrank','name','agency']

    def __str__(self):
        return '%s' % (self.name)

    def get_absolute_url(self):
        return "/wcmd/%s/measure/%s/" % (self.agency.slug, self.slug)

    def natural_key(self):
        return (self.name, self.agency)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Measure, self).save(*args, **kwargs)

class TrendReportManager(models.Manager):
    def get_by_natural_key(self, wilderness, year):
        return self.get(wilderness=wilderness, year=year)

class TrendReport(models.Model): # a group of measures to be populated for some arbitrary year

    class Direction(models.TextChoices):
        IMPROVING = 'I', _('Improving')
        STABLE = 'S', _('Stable')
        OFFSETTING_STABLE = 'O', _('Offsetting stable')
        DEGRADING = 'D', _('Degrading')

    class NextStep(models.TextChoices):
        MS = 'MS', _('measure selection')
        MA = 'MA', _('measure approval')
        ME = 'ME', _('measure entry')
        BR = 'BR', _('baseline report')
        BN = 'BN', _('baseline narrative')
        CA = 'CA', _('central approval')
        DS = 'DS', _('district signature')
        FS = 'FS', _('forest signature')

    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="trendreport_author")
    name = models.CharField('Name', max_length=80, help_text="")
    wilderness = models.ForeignKey(Wilderness, on_delete=models.PROTECT, related_name="trendreport_wilderness")
    year = models.PositiveSmallIntegerField('Report Year', help_text="")
    direction = models.CharField(
        'Trend Direction',
        max_length=1, blank=True, null=True,
        choices=Direction.choices
    )
    nextstep = models.CharField(
        'Next Step',
        max_length=3, blank=True, null=True,
        choices=NextStep.choices
    )
    remarks = models.TextField('Remarks', max_length=1024, blank=True, null=True, help_text="", )
    measures = models.ManyToManyField(Measure, blank=True, related_name="trendreport_measures")
    page_content = models.TextField(_("content"), blank=True)
    objects = TrendReportManager()

    # related: measuretrend list

    class Meta:
        verbose_name = _('trend report')
        verbose_name_plural = _('trend reports')
        unique_together = ['wilderness', 'year']
        ordering = ['wilderness','year']

    def __str__(self):
        return '%s %s %s' % (self.wilderness.agency.slug, self.wilderness.slug, self.year)

    def get_absolute_url(self):
        return "/wcmd/%s/%s/%s/" % (self.wilderness.agency.slug, self.wilderness.slug, self.year)

    def natural_key(self):
        return (self.wilderness, self.year)

class MeasureTrendManager(models.Manager):
    def get_by_natural_key(self, trendreport, measure, year):
        return self.get(trendreport=trendreport, measure=measure, year=year)

class MeasureTrend(models.Model): # a calculated trend for some measure, with a p-value where applicable

    class Direction(models.TextChoices):
        IMPROVING = 'I', _('Improving')
        STABLE = 'S', _('Stable')
        OFFSETTING_STABLE = 'O', _('Offsetting stable')
        DEGRADING = 'D', _('Degrading')

    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="measuretrend_author")
    trendreport = models.ForeignKey(TrendReport, on_delete=models.PROTECT, related_name="measuretrend_trendreport")
    measure = models.ForeignKey(Measure, on_delete=models.PROTECT, related_name="measuretrend_measure")
    remarks = models.TextField('Remarks', max_length=1024, blank=True, null=True, help_text="", )
    year = models.PositiveSmallIntegerField('Trend Year', help_text="")
    direction = models.CharField(
        'Trend Direction',
        max_length=1,
        choices=Direction.choices
    )
    formula = models.TextField('Formula', max_length=1024, blank=True, null=True, help_text="", )# how to calc trend from designation year, trend year, and selected measure values
    p_value = models.DecimalField('P-value', max_digits=7, blank=True, null=True, decimal_places=6)
    units = models.CharField('Units', max_length=80, blank=True, null=True, help_text="")
    objects = MeasureTrendManager()

    # related: measurevalue list

    class Meta:
        verbose_name = _('measure trend')
        verbose_name_plural = _('measure trends')
        unique_together = ['trendreport', 'measure', 'year']


    def __str__(self):
        return '%s %s %s %s' % (self.trendreport.wilderness.agency.slug, self.trendreport.wilderness.slug, self.trendreport.year, self.measure.slug)

    def get_absolute_url(self):
        return "/wcmd/%s/%s/%s/measure/%s/" % (self.trendreport.wilderness.agency.slug, self.trendreport.wilderness.slug, self.trendreport.year, self.measure.slug)

    def natural_key(self):
        return (self.trendreport, self.measure, self.year)

class MeasureValueManager(models.Manager):
    def get_by_natural_key(self, measuretrend, year):
        return self.get(measuretrend=measuretrend, year=year)

class MeasureValue(models.Model): # a probably annual observed value for a measure
    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="measurevalue_author")
    measuretrend = models.ForeignKey(MeasureTrend, on_delete=models.PROTECT, related_name="measurevalue_measuretrend")
    remarks = models.TextField('Remarks', max_length=1024, blank=True, null=True, help_text="", )
    cat = models.CharField('Category if CAT', max_length=80, blank=True, null=True, help_text="")
    year = models.PositiveSmallIntegerField('Value Year', help_text="")
    value = models.DecimalField("Value", max_digits=20, decimal_places=2)
    objects = MeasureValueManager()

    class Meta:
        verbose_name = _('measure value')
        verbose_name_plural = _('measure values')
        unique_together = ['measuretrend', 'year']

    def natural_key(self):
        return (self.measuretrend, self.year)

