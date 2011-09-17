from django.views.generic import DetailView
from courses.models import Arena, Course
from games.models import Game


class CourseDetailView(DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self). \
            get_context_data(**kwargs)

        context['last_games'] = Game.objects. \
            get_last_games_by_course(self.object)

        context['last_game'] = Game.objects. \
            get_last_game_by_course(self.object)

        return context


class ArenaDetailView(DetailView):
    model = Arena

    def get_context_data(self, **kwargs):
        context = super(ArenaDetailView, self). \
            get_context_data(**kwargs)

        context['last_games'] = Game.objects. \
            get_last_games_by_arena(self.object)

        context['last_game'] = Game.objects. \
            get_last_game_by_arena(self.object)

        return context
