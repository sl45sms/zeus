import functools

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect, HttpResponse
from zeus_forum.models import Post


def set_menu(menu, ctx):
    ctx['menu_active'] = menu


def common_json_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return unicode(obj)


def handle_voter_login_redirect(request, voter, default):
    _next = request.GET.get('next', None)
    _next = request.session.get('next', _next)
    _next = _next or default

    forum_post = request.GET.get('redirect_forum_post', None)
    if forum_post:
        _next = Post.objects.get(id=forum_post).url

    forum = request.GET.get('redirect_forum', None)
    if forum:
        election_uuid = voter.poll.election.uuid
        poll_uuid = voter.poll.uuid
        _next = reverse('election_poll_forum', args=(election_uuid, poll_uuid))
        _next += "#forum"

    if _next.startswith("http"):
        #TODO: prevent open redirects
        pass

    return HttpResponseRedirect(_next)

def redirects_to_linked(view):
    @functools.wraps(view)
    def wrapper(request, election, poll, *args, **kwargs):
        if request.method == 'POST':
            raise PermissionDenied
        if poll.is_linked and not poll.is_linked_root:
            root = poll.linked_to_poll
            url = request.get_full_path()
            assert poll.uuid in url
            new_url = url.replace(poll.uuid, root.uuid)
            return HttpResponseRedirect(new_url)
        return view(request, election, poll, *args, **kwargs)
    return wrapper

