from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import and_, or_, desc
from app.models.user import User as UserModel
from app.models.analytics import UserAnalytics as UserAnalyticsModel, SessionLog as SessionLogModel
from app.models.challenge import ChallengeAttempt as ChallengeAttemptModel, Challenge as ChallengeModel, ChallengeStatus
from app.models.category import Category as CategoryModel
from app.schemas.analytics import SessionLogCreate, LearningProgressResponse, LeaderboardEntry
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_analytics(self, user_id: int) -> Optional[UserAnalyticsModel]:
        """Get user analytics data"""
        return self.db.query(UserAnalyticsModel).filter(UserAnalyticsModel.user_id == user_id).first()

    def update_user_analytics(self, user_id: int) -> UserAnalyticsModel:
        """Update user analytics based on recent activity"""
        analytics = self.get_user_analytics(user_id)
        if not analytics:
            analytics = UserAnalyticsModel(user_id=user_id)
            self.db.add(analytics)

        # Calculate metrics from attempts
        attempts = self.db.query(ChallengeAttemptModel).filter(
            ChallengeAttemptModel.user_id == user_id
        ).all()

        solved_attempts = [a for a in attempts if a.is_correct]

        analytics.total_challenges_attempted = len(set(a.challenge_id for a in attempts))
        analytics.total_challenges_solved = len(set(a.challenge_id for a in solved_attempts))
        analytics.solve_rate = (analytics.total_challenges_solved / analytics.total_challenges_attempted) if analytics.total_challenges_attempted > 0 else 0

        # Calculate average solve time
        solve_times = [a.time_spent for a in solved_attempts if a.time_spent]
        if solve_times:
            analytics.avg_solve_time = sum(solve_times) / len(solve_times) / 60  # Convert to minutes
            analytics.fastest_solve_time = min(solve_times) / 60

        # Category performance (attempts vs solved per category)
        category_stats: Dict[str, Dict[str, int]] = {}
        for attempt in attempts:
            challenge = self.db.query(ChallengeModel).filter(ChallengeModel.id == attempt.challenge_id).first()
            if not challenge or not challenge.category:
                continue
            name = challenge.category.name
            if name not in category_stats:
                category_stats[name] = {"attempts": 0, "solved": 0}
            category_stats[name]["attempts"] += 1
            if attempt.is_correct:
                category_stats[name]["solved"] += 1

        if category_stats:
            analytics.category_performance = json.dumps(category_stats)

        self.db.commit()
        self.db.refresh(analytics)
        return analytics

    def create_session_log(self, user_id: int, session_data: SessionLogCreate) -> SessionLogModel:
        """Create a new session log"""
        session_log = SessionLogModel(
            user_id=user_id,
            session_id=session_data.session_id,
            user_agent=session_data.user_agent,
            ip_address=session_data.ip_address,
            device_type=session_data.device_type
        )

        self.db.add(session_log)
        self.db.commit()
        self.db.refresh(session_log)
        return session_log

    def update_session_log(self, session_id: str, user_id: int, session_data: Dict[str, Any]) -> bool:
        """Update session log with activity data"""
        session_log = self.db.query(SessionLogModel).filter(
            and_(
                SessionLogModel.session_id == session_id,
                SessionLogModel.user_id == user_id
            )
        ).first()

        if not session_log:
            return False

        # Update session data
        if 'pages_visited' in session_data:
            session_log.pages_visited = json.dumps(session_data['pages_visited'])
        if 'challenges_viewed' in session_data:
            session_log.challenges_viewed = json.dumps(session_data['challenges_viewed'])
        if 'actions_performed' in session_data:
            session_log.actions_performed = json.dumps(session_data['actions_performed'])
        if 'ended_at' in session_data:
            session_log.ended_at = datetime.fromisoformat(session_data['ended_at'])
            if session_log.started_at:
                session_log.duration = int((session_log.ended_at - session_log.started_at).total_seconds())

        self.db.commit()
        return True

    def get_user_progress(self, user_id: int) -> LearningProgressResponse:
        """Get user's learning progress"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None

        attempts = self.db.query(ChallengeAttemptModel).filter(
            ChallengeAttemptModel.user_id == user_id
        ).all()

        solved_attempts = [a for a in attempts if a.is_correct]
        total_challenges = self.db.query(ChallengeModel).filter(
            ChallengeModel.status == ChallengeStatus.ACTIVE
        ).count()

        # Build solved challenge id set
        solved_ids = set(a.challenge_id for a in solved_attempts)

        # Get ALL categories and their challenge counts
        all_categories = self.db.query(CategoryModel).all()
        category_breakdown = {}
        for cat in all_categories:
            total_in_cat = self.db.query(ChallengeModel).filter(
                and_(
                    ChallengeModel.category_id == cat.id,
                    ChallengeModel.status == ChallengeStatus.ACTIVE
                )
            ).count()
            if total_in_cat == 0:
                continue
            solved_in_cat = self.db.query(ChallengeModel).filter(
                and_(
                    ChallengeModel.category_id == cat.id,
                    ChallengeModel.id.in_(solved_ids) if solved_ids else False
                )
            ).count() if solved_ids else 0
            category_breakdown[cat.name] = {"solved": solved_in_cat, "total": total_in_cat}

        # Recent activity (last 10 attempts)
        recent_attempts = self.db.query(ChallengeAttemptModel).filter(
            ChallengeAttemptModel.user_id == user_id
        ).order_by(desc(ChallengeAttemptModel.started_at)).limit(10).all()

        recent_activity = []
        for attempt in recent_attempts:
            challenge = self.db.query(ChallengeModel).filter(ChallengeModel.id == attempt.challenge_id).first()
            status_val = attempt.status.value if hasattr(attempt.status, 'value') else attempt.status
            recent_activity.append({
                "challenge_title": challenge.title if challenge else "Unknown",
                "status": status_val,
                "points_earned": attempt.points_earned,
                "timestamp": attempt.started_at.isoformat(),
                "time_spent": attempt.time_spent
            })

        skill_level_val = user.skill_level.value if hasattr(user.skill_level, 'value') else user.skill_level
        return LearningProgressResponse(
            total_challenges=total_challenges,
            solved_challenges=len(set(a.challenge_id for a in solved_attempts)),
            current_streak=user.streak_days,
            points_earned=user.total_points,
            skill_progression={"current_level": skill_level_val, "progress": 75},
            recent_activity=recent_activity,
            category_breakdown=category_breakdown
        )

    def get_leaderboard(self, limit: int = 50, timeframe: str = "all", category_id: Optional[int] = None) -> List[LeaderboardEntry]:
        """Get leaderboard data"""
        query = self.db.query(UserModel).filter(UserModel.is_active == True)

        # Apply timeframe filter if needed
        if timeframe != "all":
            days_map = {"daily": 1, "weekly": 7, "monthly": 30}
            if timeframe in days_map:
                cutoff_date = datetime.now() - timedelta(days=days_map[timeframe])
                # This would need more complex logic to filter by timeframe

        # Order by total points and get top users
        users = query.order_by(desc(UserModel.total_points)).limit(limit).all()

        leaderboard = []
        for rank, user in enumerate(users, 1):
            # Get solve count
            solve_count = self.db.query(ChallengeAttemptModel).filter(
                and_(
                    ChallengeAttemptModel.user_id == user.id,
                    ChallengeAttemptModel.is_correct == True
                )
            ).count()

            leaderboard.append(LeaderboardEntry(
                user_id=user.id,
                username=user.username,
                display_name=user.display_name,
                total_points=user.total_points,
                level=user.level,
                solve_count=solve_count,
                rank=rank,
                avatar_url=user.avatar_url
            ))

        return leaderboard

    def get_dashboard_data(self, timeframe: str = "7d") -> Dict[str, Any]:
        """Get dashboard analytics data for admins"""
        days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(timeframe, 7)
        cutoff_date = datetime.now() - timedelta(days=days)

        # Total users
        total_users = self.db.query(UserModel).count()
        active_users = self.db.query(UserModel).filter(
            UserModel.last_activity >= cutoff_date
        ).count()

        # Challenge stats
        total_challenges = self.db.query(ChallengeModel).count()
        active_challenges = self.db.query(ChallengeModel).filter(
            ChallengeModel.status == "active"
        ).count()

        # Attempt stats
        total_attempts = self.db.query(ChallengeAttemptModel).filter(
            ChallengeAttemptModel.started_at >= cutoff_date
        ).count()

        successful_attempts = self.db.query(ChallengeAttemptModel).filter(
            and_(
                ChallengeAttemptModel.started_at >= cutoff_date,
                ChallengeAttemptModel.is_correct == True
            )
        ).count()

        return {
            "users": {
                "total": total_users,
                "active": active_users
            },
            "challenges": {
                "total": total_challenges,
                "active": active_challenges
            },
            "attempts": {
                "total": total_attempts,
                "successful": successful_attempts,
                "success_rate": (successful_attempts / total_attempts) if total_attempts > 0 else 0
            },
            "timeframe": timeframe
        }

    def get_challenge_performance(self, challenge_id: Optional[int] = None, timeframe: str = "30d") -> Dict[str, Any]:
        """Get challenge performance analytics"""
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(timeframe, 30)
        cutoff_date = datetime.now() - timedelta(days=days)

        query = self.db.query(ChallengeAttemptModel).filter(
            ChallengeAttemptModel.started_at >= cutoff_date
        )

        if challenge_id:
            query = query.filter(ChallengeAttemptModel.challenge_id == challenge_id)

        attempts = query.all()
        successful_attempts = [a for a in attempts if a.is_correct]

        # Calculate metrics
        total_attempts = len(attempts)
        successful_count = len(successful_attempts)
        success_rate = (successful_count / total_attempts) if total_attempts > 0 else 0

        # Average solve time
        solve_times = [a.time_spent for a in successful_attempts if a.time_spent]
        avg_solve_time = (sum(solve_times) / len(solve_times)) if solve_times else 0

        return {
            "total_attempts": total_attempts,
            "successful_attempts": successful_count,
            "success_rate": success_rate,
            "average_solve_time": avg_solve_time / 60 if avg_solve_time > 0 else 0,  # Convert to minutes
            "timeframe": timeframe
        }

    def get_skill_progression_insights(self, user_id: int) -> Dict[str, Any]:
        """Get skill progression insights for a user"""
        analytics = self.get_user_analytics(user_id)
        if not analytics:
            return {}

        attempts = self.db.query(ChallengeAttemptModel).filter(
            ChallengeAttemptModel.user_id == user_id
        ).order_by(ChallengeAttemptModel.started_at).all()

        # Calculate progression over time
        progression_data = []
        cumulative_solved = 0

        for attempt in attempts:
            if attempt.is_correct:
                cumulative_solved += 1

            progression_data.append({
                "date": attempt.started_at.isoformat(),
                "cumulative_solved": cumulative_solved,
                "difficulty": attempt.challenge.difficulty.value if attempt.challenge else "unknown"
            })

        return {
            "progression_timeline": progression_data,
            "current_skill_level": analytics.current_skill_level,
            "strengths": json.loads(analytics.strengths) if analytics.strengths else [],
            "weaknesses": json.loads(analytics.weaknesses) if analytics.weaknesses else [],
            "recommended_focus_areas": ["web_security", "cryptography"]  # Placeholder
        }

    def get_personalized_recommendations(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """Get personalized learning recommendations"""
        analytics = self.get_user_analytics(user_id)
        if not analytics:
            return {"challenges": [], "topics": []}

        # Get unsolved challenges based on user's skill level and preferences
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        solved_challenge_ids = self.db.query(ChallengeAttemptModel.challenge_id).filter(
            and_(
                ChallengeAttemptModel.user_id == user_id,
                ChallengeAttemptModel.is_correct == True
            )
        ).subquery()

        recommended_challenges = self.db.query(ChallengeModel).filter(
            and_(
                ChallengeModel.status == "active",
                ~ChallengeModel.id.in_(solved_challenge_ids),
                ChallengeModel.difficulty == user.skill_level
            )
        ).limit(limit).all()

        return {
            "challenges": [
                {
                    "id": c.id,
                    "title": c.title,
                    "difficulty": c.difficulty.value,
                    "points": c.points,
                    "category": c.category.name if c.category else "Unknown"
                }
                for c in recommended_challenges
            ],
            "topics": ["SQL Injection", "Buffer Overflows", "Cryptanalysis"],  # Placeholder
            "reasoning": "Based on your skill level and recent activity"
        }