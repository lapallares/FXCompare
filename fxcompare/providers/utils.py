import time


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_json(session, url, headers, params, tries=4):
    for i in range(tries):
        try:
            r = session.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )

            if r.status_code == 200:
                return r.json()

            if r.status_code == 400:
                return None

        except Exception:
            pass

        time.sleep(1.2 * (i + 1))

    return None