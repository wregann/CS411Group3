import arrow

days = []
days.append(arrow.now().shift(days=0).format('MM-DD-YYYY'))
days.append(arrow.now().shift(days=1).format('MM-DD-YYYY'))
days.append(arrow.now().shift(days=2).format('MM-DD-YYYY'))
days.append(arrow.now().shift(days=3).format('MM-DD-YYYY'))
days.append(arrow.utcnow().shift(days=4).format('MM-DD-YYYY'))

print(days)
