import os
from dotenv import load_dotenv

load_dotenv()

class Environment:
    def __init__(self):
        self.CONTAINER_NAME = os.getenv('CONTAINER_NAME', '')

        self.WS_URL = 'ws://10.247.168.43:20004/ws/connect/send/CAM_SUP'
        
        self.REDIS_HOST_INPUT = os.getenv('REDIS_HOST_INPUT', 'localhost')
        self.REDIS_PORT_INPUT = int(os.getenv('REDIS_PORT_INPUT', 6379))
        self.REDIS_DB_INPUT = os.getenv('REDIS_DB_INPUT', '0')
        self.REDIS_STREAM_KEY_INPUT = os.getenv('REDIS_STREAM_KEY_INPUT', '')



        self.SYSTEM_ID = int(os.getenv('SYSTEM_ID', 1))
        self.MINI_IMG_SCALE = float(os.getenv('MINI_IMG_SCALE', 0.15))
        self.MEDIUM_IMG_SCALE = float(os.getenv('MEDIUM_IMG_SCALE', 0.5))
        self.ORIGINAL_IMG_SCALE = float(os.getenv('ORIGINAL_IMG_SCALE', 1))

        self.LOG_PATH: str = "/system_log"
        self.IMG_PATH: str = "/system_img"

        



    def _parse_list(self, value: str) -> list[str]:
        """Recebe a STRING do env e devolve lista limpa."""
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    

    def __repr__(self) -> str:
        """Defines what is shown when printing the Environment object."""
        lines = ["\n=== Environment Variables ==="]
        for key, value in self.__dict__.items():
            lines.append(f"{key:<35}: {value}")
        lines.append("=============================\n")
        return "\n".join(lines)
