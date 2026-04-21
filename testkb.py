import ccxt
import sys

def test_crypto_bot_connection(exchange_id: str, api_key: str, secret: str, passphrase: str = None, sandbox: bool = True):
    print(f"🔍 Начинаем тест подключения к {exchange_id.upper()} (sandbox={'ON' if sandbox else 'OFF'})...")
    
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'password': passphrase,  # требуется для OKX, KuCoin, Bitget и др.
            'enableRateLimit': True,
            'sandbox': sandbox,
            'options': {'defaultType': 'spot'}
        })

        # 1. Загрузка торговых пар
        markets = exchange.load_markets()
        print(f"✅ Загружено {len(markets)} торговых пар")

        # 2. Проверка баланса (требует auth)
        balance = exchange.fetch_balance()
        non_zero = {
            k: v['free'] for k, v in balance.items()
            if isinstance(v, dict) and float(v.get('free', 0)) > 0
        }
        print("✅ Баланс получен успешно")
        if non_zero:
            print(f"💰 Ненулевые активы: {non_zero}")
        else:
            print("💡 Баланс пуст (это нормально для тестнета)")

        # 3. Проверка тикера
        symbol = list(markets.keys())[0]
        ticker = exchange.fetch_ticker(symbol)
        print(f"✅ Тикер {symbol}: Last={ticker['last']}, Volume={ticker['quoteVolume']}")

        # 4. Проверка режима песочницы
        if sandbox:
            print("🟢 Режим песочницы активен. Реальные ордера не отправляются.")
            print("✅ Тест подключения пройден успешно!")
            return True
        else:
            print("⚠️ Вы запустили тест в РЕЖИМЕ MAINNET. Убедитесь, что используете тестовые ключи.")
            return True

    except ccxt.AuthenticationError as e:
        print(f"❌ Ошибка аутентификации: {e}")
        print("🔧 Проверьте API Key / Secret / Passphrase. Ключи могут быть просрочены или отозваны.")
    except ccxt.PermissionDenied as e:
        print(f"❌ Нет прав доступа: {e}")
        print("🔧 Включите разрешения Read и Trade в настройках API. Проверьте IP-фильтр.")
    except ccxt.ExchangeNotAvailable as e:
        print(f"❌ Биржа недоступна или API изменён: {e}")
        print("🔧 Обновите ccxt: `pip install --upgrade ccxt`")
    except ccxt.RateLimitExceeded as e:
        print(f"❌ Превышен лимит запросов: {e}")
        print("🔧 Убедитесь, что `enableRateLimit: True`. Добавьте задержки между запросами.")
    except KeyError as e:
        print(f"❌ Структура ответа изменилась (биржа обновила API): {e}")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")

    return False

# 📌 Пример вызова:
test_crypto_bot_connection('binance', 'YOUR_API_KEY', 'YOUR_SECRET', sandbox=True)
test_crypto_bot_connection('bybit', 'YOUR_KEY', 'YOUR_SECRET', sandbox=True)
test_crypto_bot_connection('okx', 'YOUR_KEY', 'YOUR_SECRET', 'YOUR_PASSPHRASE', sandbox=True)