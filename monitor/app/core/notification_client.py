from abc import ABC, abstractmethod

class NotificationClient(ABC):
    """
    Interface base para clientes de notificação.
    """

    @abstractmethod
    def send_alert(self, equipment_id, alert_type, user, extra_info=None):
        """
        Envia um alerta.
        """
        pass

    @abstractmethod
    def send_text_message(self, text):
        """
        Envia uma mensagem de texto simples.
        """
        pass