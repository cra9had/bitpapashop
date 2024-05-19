from django.db import models
from .services import rub_to_btc


class TelegramUser(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    telegram_username = models.CharField(max_length=64, verbose_name="Telegram Юзернейм", null=True, blank=True)

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"

    def __str__(self):
        return f"ID {self.telegram_id}" if not self.telegram_username else f"@{self.telegram_username}"


class Transaction(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, verbose_name="Юзер")
    amount_rub = models.IntegerField(verbose_name="Сумма в руб")
    amount_btc = models.DecimalField(verbose_name="Сумма в btc", max_digits=10, decimal_places=8)
    bitpapa_code = models.CharField(verbose_name="Код bitpapa", max_length=1024, null=True, blank=True)
    is_confirmed = models.BooleanField(verbose_name="Подтверждена", default=False)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return f"{self.amount_btc} btc - {self.date_created}"


class Catalog(models.Model):
    name = models.CharField(verbose_name="Название каталога", max_length=32)

    class Meta:
        verbose_name = "Каталог"
        verbose_name_plural = "Каталоги"

    def __str__(self):
        return self.name


class Product(models.Model):
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, verbose_name="Каталог")
    name = models.CharField(verbose_name="Название товара", max_length=32)
    price_rub = models.IntegerField(verbose_name="Стоимость", help_text="в руб.")

    def in_stock(self) -> int:
        return self.content.filter(is_sold=False).count()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} | {self.price_rub} руб. | {self.in_stock()} шт."


class ProductContent(models.Model):
    body = models.TextField(verbose_name="Содержимое", max_length=4096)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар", related_name="content")
    is_sold = models.BooleanField(verbose_name="Продан", default=False)


class TelegramAccount(models.Model):
    """
    Телеграм аккаунт для обналичивания денег bitpapa
    """
    session = models.FileField(verbose_name="Сессия telethon", upload_to="media/")
    json = models.FileField(verbose_name="Json файл", upload_to="media/")
    is_banned = models.BooleanField(default=False, verbose_name="Забанен")
    balance = models.IntegerField(verbose_name="Баланс btc", default=0, help_text="btc")
    is_free = models.BooleanField(verbose_name="Свободный", default=True)

    class Meta:
        verbose_name = "Телеграм аккаут"
        verbose_name_plural = "Телеграм аккаунты"

    def __str__(self):
        return f"{self.session.name} - {self.balance} btc"


class Order(models.Model):
    STATUSES = (
        ("waiting", "В ожидании"),
        ("in_process", "Обналичивается"),
        ("bad_code", "Плохой код"),
        ("success", "Выполнен")
    )

    date_created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    buyer = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, verbose_name="Покупатель")
    order_number = models.IntegerField(verbose_name="Номер заказа", default=0)
    bitpapa_account = models.ForeignKey(TelegramAccount, on_delete=models.PROTECT, verbose_name="Обналичил аккаунт",
                                        null=True, blank=True)
    order_status = models.CharField(verbose_name="Статус заказа", choices=STATUSES, default="waiting", max_length=32)
    transaction = models.ForeignKey(Transaction, verbose_name="Транзакция", on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.order_number == 0:
            self.order_number = 13247 + self.pk
            self.save()

    def __str__(self):
        return f"Заказ #{self.order_number}"

