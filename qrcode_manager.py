# -*- coding: utf-8 -*-
"""
二维码管理器 - 用于在无GUI环境下管理登录二维码
使用文件持久化实现进程间共享
"""

import uuid
import time
import pickle
import fcntl
from pathlib import Path
from typing import Dict, Optional

class QRCodeManager:
    """全局二维码管理器，支持多个平台同时登录，使用文件持久化"""

    def __init__(self):
        # 关键修复：使用绝对路径，确保所有进程访问同一个文件
        # 基于qrcode_manager.py文件所在的目录
        project_root = Path(__file__).parent.absolute()
        self._temp_dir = project_root / "temp_qrcodes"
        self._temp_dir.mkdir(exist_ok=True)
        self._session_file = self._temp_dir / "sessions.pkl"
        self._lock_file = self._temp_dir / "sessions.lock"

        print(f"[QRCodeManager] 📂 初始化:")
        print(f"  - Project root: {project_root}")
        print(f"  - Temp dir: {self._temp_dir}")
        print(f"  - Session file: {self._session_file}")

    def _acquire_lock(self):
        """获取文件锁"""
        lock_fd = open(self._lock_file, 'w')
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        return lock_fd

    def _release_lock(self, lock_fd):
        """释放文件锁"""
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
        lock_fd.close()

    def _load_sessions(self) -> Dict[str, Dict]:
        """从文件加载所有会话"""
        if not self._session_file.exists():
            return {}

        try:
            with open(self._session_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"加载session文件失败: {e}")
            return {}

    def _save_sessions(self, sessions: Dict[str, Dict]):
        """保存所有会话到文件"""
        try:
            with open(self._session_file, 'wb') as f:
                pickle.dump(sessions, f)
        except Exception as e:
            print(f"保存session文件失败: {e}")

    def create_qrcode_session(self, platform: str, base64_image: str, expiry_seconds: int = 300) -> str:
        """
        创建二维码会话

        Args:
            platform: 平台名称 (weibo, xhs, douyin等)
            base64_image: base64编码的二维码图片
            expiry_seconds: 有效期（秒），默认5分钟

        Returns:
            session_id: 会话ID，用于访问二维码页面
        """
        session_id = str(uuid.uuid4())

        print(f"[QRCodeManager] 🔵 创建新会话:")
        print(f"  - Session ID: {session_id}")
        print(f"  - Platform: {platform}")
        print(f"  - Image length: {len(base64_image) if base64_image else 0}")
        print(f"  - Session file: {self._session_file}")

        lock_fd = self._acquire_lock()
        try:
            # 关键修复：保存前重新加载，确保不覆盖其他进程的更新
            sessions = self._load_sessions()
            print(f"[QRCodeManager] 📂 加载现有sessions (保存前): {len(sessions)} 个")
            print(f"[QRCodeManager] 📋 现有IDs: {list(sessions.keys())}")

            sessions[session_id] = {
                'platform': platform,
                'base64_image': base64_image,
                'created_at': time.time(),
                'expiry_seconds': expiry_seconds,
                'scanned': False,
                'login_success': False
            }

            print(f"[QRCodeManager] 💾 保存session到文件 (含新session)...")
            self._save_sessions(sessions)
            print(f"[QRCodeManager] ✅ Session保存成功，当前共 {len(sessions)} 个")

            # 验证保存
            verify_sessions = self._load_sessions()
            print(f"[QRCodeManager] 🔍 验证: 文件中现有 {len(verify_sessions)} 个sessions")
            print(f"[QRCodeManager] 📋 验证IDs: {list(verify_sessions.keys())}")

            if session_id in verify_sessions:
                print(f"[QRCodeManager] ✅ Session验证成功: {session_id}")
            else:
                print(f"[QRCodeManager] ❌ Session验证失败: {session_id} 未找到!")
                print(f"[QRCodeManager] ⚠️  可能被其他进程覆盖了!")

        finally:
            self._release_lock(lock_fd)

        return session_id

    def get_qrcode(self, session_id: str) -> Optional[Dict]:
        """获取二维码信息"""
        print(f"[QRCodeManager] 🔍 查询Session: {session_id}")
        print(f"  - Session file: {self._session_file}")
        print(f"  - File exists: {self._session_file.exists()}")

        lock_fd = self._acquire_lock()
        try:
            sessions = self._load_sessions()
            print(f"[QRCodeManager] 📂 加载sessions: {len(sessions)} 个")
            print(f"[QRCodeManager] 📋 所有session IDs: {list(sessions.keys())}")

            qrcode_info = sessions.get(session_id)

            if not qrcode_info:
                print(f"[QRCodeManager] ❌ Session未找到: {session_id}")
                return None

            print(f"[QRCodeManager] ✅ Session找到!")
            print(f"  - Platform: {qrcode_info.get('platform')}")
            print(f"  - Created: {qrcode_info.get('created_at')}")

            # 检查是否过期
            elapsed = time.time() - qrcode_info['created_at']
            print(f"  - Elapsed: {elapsed:.1f}s / {qrcode_info['expiry_seconds']}s")

            if elapsed > qrcode_info['expiry_seconds']:
                # 过期则删除 - 关键修复：删除前重新加载，避免覆盖其他进程的更新
                print(f"[QRCodeManager] ⏰ Session已过期，删除中...")
                print(f"[QRCodeManager] 🔄 重新加载sessions以避免覆盖...")
                sessions = self._load_sessions()  # 重新加载最新数据
                print(f"[QRCodeManager] 📂 重新加载后: {len(sessions)} 个sessions")
                print(f"[QRCodeManager] 📋 IDs: {list(sessions.keys())}")

                if session_id in sessions:
                    del sessions[session_id]
                    print(f"[QRCodeManager] 🗑️  删除过期session: {session_id}")
                else:
                    print(f"[QRCodeManager] ⚠️  Session已被其他进程删除")

                self._save_sessions(sessions)
                print(f"[QRCodeManager] 💾 保存后剩余: {len(sessions)} 个sessions")
                return None

            return qrcode_info
        finally:
            self._release_lock(lock_fd)

    def mark_login_success(self, session_id: str) -> bool:
        """标记登录成功"""
        lock_fd = self._acquire_lock()
        try:
            # 关键修复：保存前重新加载，确保不覆盖其他进程的更新
            sessions = self._load_sessions()

            if session_id in sessions:
                sessions[session_id]['login_success'] = True
                # 再次加载最新数据后再修改和保存
                sessions = self._load_sessions()
                if session_id in sessions:
                    sessions[session_id]['login_success'] = True
                    self._save_sessions(sessions)
                    return True
            return False
        finally:
            self._release_lock(lock_fd)

    def is_login_success(self, session_id: str) -> bool:
        """检查是否登录成功"""
        lock_fd = self._acquire_lock()
        try:
            sessions = self._load_sessions()
            qrcode_info = sessions.get(session_id)
            if qrcode_info:
                return qrcode_info.get('login_success', False)
            return False
        finally:
            self._release_lock(lock_fd)

    def cleanup_expired(self):
        """清理过期的二维码会话"""
        lock_fd = self._acquire_lock()
        try:
            # 关键修复：删除前重新加载最新数据
            sessions = self._load_sessions()
            current_time = time.time()

            expired_sessions = [
                sid for sid, info in sessions.items()
                if current_time - info['created_at'] > info['expiry_seconds']
            ]

            if expired_sessions:
                # 重新加载以避免覆盖其他进程的更新
                sessions = self._load_sessions()
                for sid in expired_sessions:
                    if sid in sessions:  # 再次检查，可能已被其他进程删除
                        del sessions[sid]

                self._save_sessions(sessions)
        finally:
            self._release_lock(lock_fd)

    def get_all_sessions(self) -> Dict:
        """获取所有活跃会话（调试用）"""
        lock_fd = self._acquire_lock()
        try:
            sessions = self._load_sessions()
            return {
                sid: {
                    'platform': info['platform'],
                    'created_at': info['created_at'],
                    'login_success': info['login_success']
                }
                for sid, info in sessions.items()
            }
        finally:
            self._release_lock(lock_fd)

# 全局单例
_qrcode_manager = None

def get_qrcode_manager() -> QRCodeManager:
    """获取全局二维码管理器实例"""
    global _qrcode_manager
    if _qrcode_manager is None:
        _qrcode_manager = QRCodeManager()
    return _qrcode_manager
