def calculate_user_stats(user_quizzes):
    total_quizzes = len(user_quizzes)
    if total_quizzes == 0:
        return {
            "totalQuizzes": 0,
            "averageScore": 0,
            "bestScore": 0,
            "totalStars": 0,
            "streak": 0,
            "level": "Новичок",
            "rank": 0,
            "recentQuizzes": [],
            "categoryStats": [],
        }

    average_score = sum(q.percentage for q in user_quizzes) / total_quizzes
    best_score = max(q.percentage for q in user_quizzes)
    total_stars = sum(q.stars_earned for q in user_quizzes)

    # Streak calculation
    dates = sorted(set(q.completed_at.date() for q in user_quizzes))
    streak = 0
    max_streak = 0
    last_date = None
    for d in dates:
        if last_date is None or (d - last_date).days == 1:
            streak += 1
        else:
            streak = 1
        max_streak = max(max_streak, streak)
        last_date = d

    # Level calculation
    if average_score >= 90:
        level = "Эксперт"
    elif average_score >= 75:
        level = "Продвинутый"
    elif average_score >= 50:
        level = "Средний"
    else:
        level = "Новичок"

    rank = 999

    recent_quizzes = sorted(user_quizzes, key=lambda q: q.completed_at, reverse=True)[:5]
    recent_quizzes_data = [
        {
            "quiz_id": q.quiz_id,
            "title": q.title,
            "category": q.category,
            "percentage": q.percentage,
            "completed_at": q.completed_at.isoformat(),
        } for q in recent_quizzes
    ]

    categories = {}
    for q in user_quizzes:
        cat = q.category
        if cat not in categories:
            categories[cat] = {"quizzes": 0, "stars": 0}
        categories[cat]["quizzes"] += 1
        categories[cat]["stars"] += q.stars_earned
    category_stats = [
        {"category": cat, "totalQuizzes": val["quizzes"], "totalStars": val["stars"]}
        for cat, val in categories.items()
    ]

    return {
        "totalQuizzes": total_quizzes,
        "averageScore": round(average_score, 2),
        "bestScore": round(best_score, 2),
        "totalStars": total_stars,
        "streak": max_streak,
        "level": level,
        "rank": rank,
        "recentQuizzes": recent_quizzes_data,
        "categoryStats": category_stats,
    }