def welcome(request):
    """Добавляет в контекст переменную greeting с приветствием."""
    return {
        'greeting': 'Ennyn Pronin: pedo mellon a minno.',
    }
