from django.views.generic import DetailView
from courses.models import Arena, Course
from games.models import Game


class DetailViewGameContext(DetailView):
    def get_context_data(self, **kwargs):
        context = super(DetailView, self). \
            get_context_data(**kwargs)

        context['last_games'] = Game.objects. \
            get_last_games_by_course(self.object)

        context['last_game'] = Game.objects. \
            get_last_games_by_course(self.object, only_latest=True)

        return context


class CourseDetailView(DetailViewGameContext):
    model = Course


class ArenaDetailView(DetailViewGameContext):
    model = Arena
