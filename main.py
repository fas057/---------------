# Импорт необходимых библиотек для работы приложения

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Email


app = Flask(__name__, template_folder='templates')
# Подключение к БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db' # путь к БД
app.config['SECRET_KEY'] = 'anton'  # используется для установки секретного ключа в конфигурации приложения Flask
db = SQLAlchemy(app) # создает экземпляр SQLAlchemy, который связывается с приложением Flask

# Модель для записей о клиентах
class Clients(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    message = db.Column(db.Text, nullable = False)
    phone = db.Column (db.Integer, nullable = False)

# Возвращает строку, представляющую объект clients, с указанием значений его атрибутов имени, эл.почты, запроса и телефона
    def __repr__(self):
        return f"Clients(name='{self.name}', email='{self.email}', message='{self.message}', phone='{self.phone}')"

# Форма записи для клиентов
class ClientsForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Опишите Ваш запрос', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Записаться')

# Маршрут к главной странице
@app.route('/')
def home():
    return render_template('index.html')

# Маршрут к странице с формой
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ClientsForm() #  создаем экземпляр формы
    if form.validate_on_submit(): # проверяем, была ли форма отправлена и прошла ли валидацию с помощью метода form.validate_on_submit
        name = form.name.data
        email = form.email.data
        message = form.message.data
        phone = form.phone.data
# если форма прошла валидацию, то мы получаем данные из формы (имя, email,запрос и телефон) и создаем новую запись в базе данных с использованием модели Clients
        clients = Clients(name=name, email=email, message=message, phone=phone)
        # сохраняем запись в базе данных 
        db.session.add(clients)
        db.session.commit()
# после успешного сохранения записи, перенаправляем пользователя на страницу success.html
        return redirect(url_for('success'))
# если форма не прошла валидацию, мы рендерим шаблон contact.html и передаем в него экземпляр формы form.
    return render_template('contact.html', form=form)

# Маршрут к странице с таблицей пользователей
@app.route('/users')
def users():
    users = Clients.query.all() # извлекает все записи из таблицы Clients в базе данных и сохраняет их в переменной users.
    return render_template('users.html', users=users) # вызывает функцию render_template() для отображения шаблона users.html и передает ему переменную users, содержащую список записей о пользователях

# Маршрут к странице с добавлением пользователей
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    form = ClientsForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        phone = form.phone.data

        clients = Clients(name=name, email=email, message=message,phone=phone)
        db.session.add(clients)
        db.session.commit()

        return redirect(url_for('users'))
    
    return render_template('add_user.html', form=form)

# Маршрут к странице с редактированием пользователей
@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = Clients.query.get_or_404(id) # получаем запись пользователя из базы данных с использованием Clients.query.get_or_404(id). Если запись не найдена, сервер вернет ошибку 404
    form = ClientsForm(obj=user) # создаем экземпляр формы ClientsForm(obj=user). obj=user позволяет предзаполнить значения формы данными из записи пользователя
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.message = form.message.data
        user.phone = form.phone.data

        db.session.commit()

        return redirect(url_for('users'))

    return render_template('edit_user.html', form=form)

# Маршрут к странице с удалением пользователей (фактически удаление происходит на странице users, без подтверждения)
@app.route('/users/delete/<int:id>')
def delete_user(id):
    user = Clients.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('users'))


# Маршрут к странице с успешной отправкой формы
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__': # проверяется, является ли текущий скрипт главным т.е. запущен ли он напрямую, а не импортирован из другого модуля
    app.run(debug=True) # указывает, что приложение будет работать в режиме отладки
