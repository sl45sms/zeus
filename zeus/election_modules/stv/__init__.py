import json

from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory
from django.forms import ValidationError
from django.http import HttpResponseRedirect

from zeus.election_modules import ElectionModuleBase, election_module
from zeus.views.utils import set_menu

from helios.view_utils import render_template


@election_module
class StvElection(ElectionModuleBase):
    module_id = 'stv'
    description = _('Single Transferable Vote Election')
    messages = {
        'answer_title': _('Candidate'),
        'question_title': _('Candidates List')
    }
    auto_append_answer = True
    count_empty_question = False
    booth_questions_tpl = 'question_ecounting'
    no_questions_added_message = _('No questions set')

    def questions_update_view(self, request, election, poll):
        from zeus.utils import poll_reverse
        from zeus.forms import StvForm, DEFAULT_ANSWERS_COUNT, \
                MAX_QUESTIONS_LIMIT

        if not poll.questions_data:
            poll.questions_data = [{}]

        poll.questions_data[0]['departments_data'] = election.departments
        initial = poll.questions_data

        extra = 1
        if poll.questions_data:
            extra = 0

        questions_formset = formset_factory(StvForm, extra=extra,
                                            can_delete=True, can_order=True)


        if request.method == 'POST':
            formset = questions_formset(request.POST, initial=initial)
            if formset.is_valid():
                questions_data = []
                for question in formset.cleaned_data:
                    if not question:
                        continue
                    # force sort of answers by extracting index from answer key.
                    # cast answer index to integer, otherwise answer_10 would
                    # be placed before answer_2
                    answer_index = lambda a: int(a[0].replace('answer_', ''))
                    isanswer = lambda a: a[0].startswith('answer_')

                    answer_values = filter(isanswer, question.iteritems())
                    sorted_answers = sorted(answer_values, key=answer_index)

                    answers = [json.loads(x[1])[0] for x in sorted_answers]
                    departments = [json.loads(x[1])[1] for x in sorted_answers]

                    final_answers = []
                    for a,d in zip(answers, departments):
                        final_answers.append(a+':'+d)
                    question['answers'] = final_answers
                    for k in question.keys():
                        if k in ['DELETE', 'ORDER']:
                            del question[k]

                    questions_data.append(question)

                poll.questions_data = questions_data
                poll.update_answers()
                poll.logger.info("Poll ballot updated")
                poll.save()

                url = poll_reverse(poll, 'questions')
                return HttpResponseRedirect(url)
        else:
            formset = questions_formset(initial=initial)

        context = {
            'default_answers_count': DEFAULT_ANSWERS_COUNT,
            'formset': formset,
            'max_questions_limit': 1,
            'election': election,
            'poll': poll,
            'module': self
        }
        set_menu('questions', context)

        tpl = 'election_modules/stv/election_poll_questions_manage'
        return render_template(request, tpl, context)

    def update_answers(self):
        answers = []
        questions_data = self.poll.questions_data or []
        prepend_empty_answer = True
        if self.auto_append_answer:
            prepend_empty_answer = True
        for index, q in enumerate(questions_data):
            q_answers = ["%s" % (ans) for ans in \
                         q['answers']]
            group = index 
            if prepend_empty_answer:
                #remove params and q questions
                params_max = len(q_answers) 
                params_min = 0 
                if self.count_empty_question:
                    params_min = 0
                params = "%d-%d, %d" % (params_min, params_max, group)
                q_answers.insert(0, "%s: %s" % (q.get('question'), params))
            answers = answers + q_answers
        answers = questions_data[0]['answers']
        self.poll._init_questions(len(answers))
        self.poll.questions[0]['answers'] = answers
    def compute_results(self):
        self.poll.generate_result_docs()

    def get_booth_template(self, request):
        raise NotImplemented
