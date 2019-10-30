def generate_user_text(db_user_object):
    """
    Сгенерировать текст анкеты пользователя
    """
    gender_text = ''
    if db_user_object.gender == 0 or db_user_object.gender == False:
        gender_text = 'Мужчина'
    elif db_user_object == 1 or db_user_object.gender == True:
        gender_text = 'Женщина'

    return 'Имя: {!s}\n\nВозраст: {!s}\n\nПол: {!s}\n\nОбо мне: {!s}'.format(
        db_user_object.name, db_user_object.age, gender_text, db_user_object.about
    )
