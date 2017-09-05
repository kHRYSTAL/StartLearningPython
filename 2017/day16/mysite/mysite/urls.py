"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

# url映射 调用app中的views就可以
from myapp import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'h.html', views.home)

    url(r'^login', views.login),  # 注意:login后如果有/ 模版文件提交表单也必须加 两者必须一致
    url(r'^home', views.home),
]