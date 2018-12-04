from django.contrib import admin
from import_export.admin import ImportExportModelAdmin 
from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )


# admin.site.register(Census, CensusAdmin)

@admin.register(Census)
class ViewAdmin(ImportExportModelAdmin):
    pass