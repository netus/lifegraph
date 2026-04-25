from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LifeNodeQuickCreateForm
from .models import LifeNode, NodeParticipant


@login_required(login_url=f"/{settings.ADMIN_URL}/login/")
def timeline_view(request):
    nodes = LifeNode.objects.filter(owner=request.user).order_by("-occurred_at", "-id")

    if request.method == "POST":
        form = LifeNodeQuickCreateForm(request.POST)
        if form.is_valid():
            node = form.save(commit=False)
            node.owner = request.user
            node.what = node.raw_text
            node.privacy = LifeNode.Privacy.PRIVATE
            node.source_type = LifeNode.SourceType.TEXT
            node.save()
            NodeParticipant.objects.get_or_create(
                node=node,
                user=request.user,
                defaults={
                    "display_name": request.user.get_full_name() or request.user.get_username(),
                    "status": NodeParticipant.Status.SELF,
                },
            )
            return redirect("/")
    else:
        form = LifeNodeQuickCreateForm()

    return render(request, "lifegraph/timeline.html", {"form": form, "nodes": nodes})


def bad_request_handler(request, exception):
    return render(request, "lifegraph/error.html", {"status_code": 400}, status=400)


def permission_denied_handler(request, exception):
    return render(request, "lifegraph/error.html", {"status_code": 403}, status=403)


def not_found_handler(request, exception):
    return render(request, "lifegraph/error.html", {"status_code": 404}, status=404)


def server_error_handler(request):
    return render(request, "lifegraph/error.html", {"status_code": 500}, status=500)
