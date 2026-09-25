from django.contrib import admin
from .models import (Author, AuthorDetail, Book, Borrow, Category, Event,
                     EventParticipant, Library, Member, Posts, Review)

admin.site.site_header = 'Управление библиотеками'
admin.site.site_title = 'Библиотеки'
admin.site.index_title = 'Практикум Django: модели'


class AuthorDetailInline(admin.StackedInline):
    model = AuthorDetail
    extra = 0


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'rating', 'deleted')
    search_fields = ('first_name', 'last_name')
    list_filter = ('deleted', 'rating')
    inlines = (AuthorDetailInline,)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publishing_date', 'publisher', 'category')
    search_fields = ('title', 'author__last_name')
    list_filter = ('genre', 'category', 'libraries')
    autocomplete_fields = ('author', 'publisher', 'category')
    filter_horizontal = ('libraries',)
    readonly_fields = ('rating',)
    list_select_related = ('author', 'publisher', 'category')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role', 'active')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('role', 'active', 'libraries')
    filter_horizontal = ('libraries',)


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'site')
    search_fields = ('name', 'location')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'library', 'moderated', 'created_at')
    list_filter = ('moderated', 'library')
    search_fields = ('title', 'body')
    autocomplete_fields = ('author', 'library')
    readonly_fields = ('updated_at',)
    date_hierarchy = 'created_at'


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'library', 'borrow_date', 'return_date', 'returned', 'overdue')
    list_filter = ('returned', 'library')
    autocomplete_fields = ('book', 'member', 'library')

    @admin.display(boolean=True, description='Просрочена')
    def overdue(self, obj):
        return obj.is_overdue()


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'reviewer', 'rating')
    autocomplete_fields = ('book', 'reviewer')


@admin.register(AuthorDetail)
class AuthorDetailAdmin(admin.ModelAdmin):
    list_display = ('author', 'birth_city', 'gender')
    autocomplete_fields = ('author',)


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 0
    autocomplete_fields = ('member',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'library')
    search_fields = ('title',)
    list_filter = ('library',)
    autocomplete_fields = ('library',)
    filter_horizontal = ('books',)
    inlines = (EventParticipantInline,)


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'member', 'registration_date')
    autocomplete_fields = ('event', 'member')
