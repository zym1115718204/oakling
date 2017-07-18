from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()


logger_api_urls = patterns("clawer.apis.logger", url(r"^all/$", "all"), )

monitor_api_urls = patterns("clawer.apis.monitor",
                            url(r"^task/stat/$", "task_stat"),
                            url(r"^hour/$", "hour"),
                            url(r"^day/$", "day"),
                            url(r"^hour/echarts/$", "hour_echarts"),
                            url(r"^day/echarts/$", "day_echarts"), )

home_api_urls = patterns("clawer.apis.home",
                         url(r"^clawer/all/$", "clawer_all"),
                         url(r"^clawer/add/$", "clawer_add"),
                         url(r"^clawer/task/$", "clawer_task"),
                         url(r"^clawer/task/add/$", "clawer_task_add"),
                         url(r"^clawer/task/reset/$", "clawer_task_reset"),
                         url(r"^clawer/task/generator/update/$", "clawer_task_generator_update"),
                         url(r"^clawer/task/generator/history/$", "clawer_task_generator_history"),
                         url(r"^clawer/generate/log/$", "clawer_generate_log"),
                         url(r"^clawer/analysis/history/$", "clawer_analysis_history"),
                         url(r"^clawer/analysis/log/$", "clawer_analysis_log"),
                         url(r"^clawer/analysis/update/$", "clawer_analysis_update"),
                         url(r"^clawer/setting/update/$", "clawer_setting_update"),
                         url(r"^clawer/download/log/$", "clawer_download_log"), )
# views
logger_urls = patterns("clawer.views.logger", url(r"^$", "index"), )

monitor_urls = patterns("clawer.views.monitor",
                        url(r"^realtime/dashboard/$", "realtime_dashboard"),
                        url(r"^hour/$", "hour"),
                        url(r"^day/$", "day"), )


# Web2.0 apis

user_api_urls = patterns("clawer.apis.user",
                         url(r"^login/$", "login"),
                         url(r"^login_dashboard/$", "login_dashboard"),
                         url(r"^logout/$", "logout"),
                         url(r"^keepalive/$", "keepalive"),
                         url(r"^is/logined/$", "is_logined"),
                         url(r"^my/menus/$", "get_my_menus"), )

rest_api_urls = patterns("clawer.apis.rest",
                         url(r"^v1/enterprise$", "enterprise"),
                         url(r"^v2/enterprise$", "enterprise_v2"),
                         url(r"^v1/general$", "general"), )

query_api_urls = patterns("clawer.apis.query",
                         url(r"^tasks$", "clawer_tasks"),
                         url(r"^task/(?P<task_id>\w+)/$", "clawer_task_item"),
                         url(r"^enterprise$", "enterprise"),
                         )

search_api_urls = patterns("clawer.apis.search",
                           url(r"^v1/enterprise$", "search_enterprise_list"),
                           )

command_api_urls = patterns("clawer.apis.command",
                           url(r"^open/$",  "open_job"),
                           url(r"^close/$", "close_job"),
                           url(r"^update/$", "update_job"),
                           url(r"^reset/$", "reset_task"),
                           )

apis_urls = patterns("clawer.apis",
                     url(r"^user/", include(user_api_urls)),
                     url(r"^home/", include(home_api_urls)),
                     url(r"^logger/", include(logger_api_urls)),
                     url(r"^monitor/", include(monitor_api_urls)),
                     url(r"^rest/", include(rest_api_urls)),
                     url(r"^query/", include(query_api_urls)),
                     url(r"^search/", include(search_api_urls)),
                     url(r"^command/", include(command_api_urls)),
                     )

dashboard_urls = patterns("clawer.views.dashboard",
                          url(r"^$", "index"),
                          url(r"^clawer/$", "clawer"),
                          url(r"^debug/(?P<job_id>\w+)/$", "debug"),
                          # url(r"^items/$", "items"),
                          url(r'^accounts/login/', 'login'),
                          url(r'^items/(?P<job_id>\w+)/$', 'item_detail'),
                          # 403
                          url(r'^403/', 'page_403'),
                          url(r'^404/', 'page_404'),
                          url(r'^500/', 'page_500'),
                          )

search_urls = patterns("clawer.views.search",
                          url(r"^$", "index"),
                          url(r'^search_enterprise$', 'search_enterprise'),
                          url(r'^accounts/login/', 'login'),
                          url(r'^detail$', 'enterprise_detail'),
                          # url(r'^detail/(?P<task_id>\w+)/$', 'task_detail'),
                          url(r'^403/', 'page_403'),
                          url(r'^404/', 'page_404'),
                          url(r'^500/', 'page_500'),
                          )

urlpatterns = patterns('clawer.views.home',
                       url(r'^$', 'index'),
                       url(r'^clawer/$', "clawer"),
                       url(r'^clawer/all/$', "clawer_all"),
                       url(r"^clawer/download/log/$", "clawer_download_log"),
                       url(r"^clawer/task/$", "clawer_task"),
                       url(r"^clawer/analysis/log/$", "clawer_analysis_log"),
                       url(r"^clawer/generate/log/$", "clawer_generate_log"),
                       url(r"^clawer/setting/$", "clawer_setting"),
                       url(r"^logger/", include(logger_urls)),
                       url(r"^monitor/", include(monitor_urls)),
                       url(r'^apis/', include(apis_urls)),
                       url(r'^dashboard/', include(dashboard_urls)),
                       url(r"^captcha/", include("captcha.urls")),
                       url(r'^search/', include(search_urls)),
                       url(r"^enterprise/", include("enterprise.urls")),

                       url(r'^admin/', include(admin.site.urls)), )

if settings.DEBUG:
    urlpatterns += patterns(
        "",
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,
                                                                'show_indexes': True}), )

handler404 = 'clawer.views.dashboard.page_404'
handler500 = 'clawer.views.dashboard.page_500'
