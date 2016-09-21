import os

import click

from cli.form import CLIFormWrapper
from medicover import Medicover
from visit_scheduler import VisitPreference


VISIT_PREFERENCE_PARAMS_DATA = (
    ('time_from', 'Not before hour? FORMAT: HH:MM e.g. 12:00'),
    ('time_to', 'Not after hour? FORMAT: HH:MM e.g. 12:00'),
    ('date_from', 'Not before date? FORMAT: DD.MM.YYYY eg. 01.01.2016'),
    ('date_to', 'Not after date? FORMAT: DD.MM.YYYY eg. 01.01.2016'),
    ('weekday', 'What day of the week? FORMAT: full weekday name e.g. wednesday')
)


@click.group()
@click.option('-u', default=lambda: os.environ.get('MEDICOVER_USER'), show_default=False,
              help='Your Medicover card number')
@click.option('-p', default=lambda: os.environ.get('MEDICOVER_PASSWORD'), show_default=False,
              help='Your Medicover password')
@click.pass_context
def medicover(ctx, u, p):
    ctx.obj['M'] = Medicover(user=u, password=p)


@medicover.command()
@click.pass_context
def search(ctx):
    m = ctx.obj['M']
    cli_form = CLIFormWrapper(m.form)
    cli_form.start()
    m.form.search()
    while True:
        click.echo('\n'.join('{:d}: {:s}'.format(index, visit) for index, visit in enumerate(m.form.results)))
        if click.confirm('Would you like to load more results'):
            m.form.load_more()
        else:
            break
    if click.confirm('Would you like to book a visit?'):
        visit_to_book_index = click.prompt('Which visit would you like to book?', type=int)
        visit = m.form.results[visit_to_book_index]
        booked_ok = visit.book()
        click.echo('Visit booked successfully' if booked_ok else 'Booking failed')
    else:
        if click.confirm('Would you like to create a visit preference from your search?'):
            visit_preference_data = prompt_for_visit_preference_data()
            vp = VisitPreference(m.form.request_params, **visit_preference_data)


def prompt_for_visit_preference_data():
    click.echo('Please provide visit preference details. Press ENTER to skip a field')
    params = {}
    for param_name, help_text in VISIT_PREFERENCE_PARAMS_DATA:
        value = click.prompt(help_text, default='')
        if value:
            params[param_name] = value
    return params


def main():
    return medicover(obj={})