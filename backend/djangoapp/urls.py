"""
URL configuration for djangoapp project.

Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# register all blueprint/app route
urlpatterns = [
    path('api-v2/admin/', admin.site.urls),
    path('api-v2/users/', include('users.urls')),
    path('api-v2/chat/', include('chats.urls')),
]
