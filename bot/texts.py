WELCOME = (
    "Добро пожаловать! ✨\n\n"
    "Выберите категорию или посмотрите контакты."
)

CONTACTS_DEFAULT = (
    "📞 Контакты\n\n"
    "Напишите мне в Telegram — контакты пока не настроены."
)

EMPTY_CATEGORY = "В этой категории пока пусто 🙈"

ORDER_INSTRUCTION = (
    "🛍️ Супер! Чтобы заказать:\n\n"
    "1. Нажмите на фото 📸\n"
    "2. Сделайте скриншот\n"
    "3. Напишите мне в ЛС\n"
    "4. Пришлите фото и название товара"
)

ADMIN_WELCOME = (
    "🔧 Админ-панель\n\n"
    "Управление каталогом и настройками."
)

ADMIN_ACCESS_DENIED = "У вас нет доступа к админ-панели."

CATEGORY_ADD_PROMPT = "Введите название новой категории:"
CATEGORY_ADDED = "✅ Категория «{title}» добавлена."
CATEGORY_DELETED = "✅ Категория и все её товары удалены."
CATEGORY_DELETE_CONFIRM = (
    "⚠️ Удалить категорию «{title}»?\n"
    "Будет удалено товаров: {count}\n\n"
    "Подтвердите удаление."
)

PRODUCT_ADD_CATEGORY = "Выберите категорию для товара:"
PRODUCT_ADD_PHOTO = (
    "Отправьте фото товара.\n"
    "Можно отправить несколько — по одному или альбомом.\n"
    "Когда закончите, нажмите «✅ Готово»."
)
PRODUCT_ADD_PHOTO_ADDED = "Фото добавлено ({count}). Отправьте ещё или нажмите «✅ Готово»."
PRODUCT_ADD_PHOTO_REQUIRED = "Нужно хотя бы одно фото."
PRODUCT_ADD_TITLE = "Введите название товара:"
PRODUCT_ADD_DESCRIPTION = "Введите описание:"
PRODUCT_ADD_PRICE = "Введите цену (текстом, например: 1500 ₽):"
PRODUCT_ADD_SORT = "Введите порядок сортировки (число, меньше — выше в списке):"
PRODUCT_ADD_CONFIRM = (
    "Проверьте товар:\n\n"
    "📁 {category}\n"
    "📌 {title}\n"
    "💰 {price}\n"
    "🔢 sort: {sort_order}\n\n"
    "{description}"
)
PRODUCT_ADDED = "✅ Товар добавлен."
PRODUCT_DELETED = "✅ Товар удалён."
PRODUCT_UPDATED = "✅ Сохранено."

CONTACTS_EDIT_PROMPT = "Отправьте новый текст для раздела «Контакты»:"
CONTACTS_UPDATED = "✅ Контакты обновлены."

MENU_TEXT_EDIT_PROMPT = "Отправьте новый текст для главного меню (/start):"
MENU_TEXT_UPDATED = "✅ Текст меню обновлён."

PRODUCT_PHOTOS_TITLE = "📷 Фото товара «{title}» ({count} шт.)"
PRODUCT_PHOTO_ADDED = "✅ Фото добавлено."
PRODUCT_PHOTO_DELETED = "✅ Фото удалено."
PRODUCT_PHOTO_DELETE_BLOCKED = "Нельзя удалить последнее фото — у товара должно остаться хотя бы одно."
PRODUCT_PHOTO_ADD_PROMPT = "Отправьте фото для добавления:"
PRODUCT_PHOTO_DELETE_CONFIRM = "Удалить это фото?"

CANCELLED = "Отменено."
INVALID_INPUT = "Некорректный ввод. Попробуйте снова."
