# animations.py
"""Система анимаций для ScrabbleGame"""

import tkinter as tk
import math
from typing import Callable, List, Tuple
from ui_styles import Colors, Fonts


class Animation:
    """Базовый класс для анимаций"""
    
    def __init__(self, duration: int = 500):
        """
        Args:
            duration: Длительность анимации в миллисекундах
        """
        self.duration = duration
        self.start_time = 0
        self.is_running = False
    
    def start(self):
        """Запускает анимацию"""
        self.is_running = True
        self.start_time = 0
    
    def update(self, elapsed: int) -> bool:
        """
        Обновляет состояние анимации.
        
        Args:
            elapsed: Прошедшее время в мс
            
        Returns:
            True если анимация завершена
        """
        return elapsed >= self.duration
    
    def stop(self):
        """Останавливает анимацию"""
        self.is_running = False


class FadeInAnimation(Animation):
    """Анимация плавного появления (изменение прозрачности)"""
    
    def __init__(self, canvas: tk.Canvas, item_id: int, duration: int = 300):
        super().__init__(duration)
        self.canvas = canvas
        self.item_id = item_id
        self.original_color = None
    
    def get_alpha(self, progress: float) -> float:
        """Возвращает альфа-канал (0.0 - 1.0) для прогресса анимации"""
        return min(1.0, progress)


class ScorePopupAnimation(Animation):
    """Анимация всплывающего текста с очками"""
    
    def __init__(self, canvas: tk.Canvas, x: int, y: int, score: int, duration: int = 1000):
        super().__init__(duration)
        self.canvas = canvas
        self.start_x = x
        self.start_y = y
        self.score = score
        self.text_id = None
        
        # Создаем текст
        self.text_id = canvas.create_text(
            x, y,
            text=f"+{score}",
            font=Fonts.SCORE,
            fill=Colors.SUCCESS,
            anchor="center"
        )
    
    def update(self, elapsed: int) -> bool:
        """Обновляет позицию всплывающего текста"""
        if not self.text_id:
            return True
        
        progress = elapsed / self.duration
        
        # Движение вверх с замедлением
        offset_y = -50 * self.easeOutQuad(progress)
        
        # Изменение прозрачности (fade out в конце)
        if progress > 0.7:
            alpha = 1.0 - (progress - 0.7) / 0.3
        else:
            alpha = 1.0
        
        # Обновляем позицию
        self.canvas.coords(self.text_id, self.start_x, self.start_y + offset_y)
        
        # Изменяем размер (растет в начале)
        if progress < 0.3:
            scale = 1.0 + progress
            size = int(12 * scale)
            self.canvas.itemconfig(self.text_id, font=("Segoe UI", size, "bold"))
        
        if progress >= 1.0:
            self.canvas.delete(self.text_id)
            return True
        
        return False
    
    @staticmethod
    def easeOutQuad(t: float) -> float:
        """Функция замедления"""
        return t * (2 - t)


class PulseAnimation(Animation):
    """Анимация пульсации (масштабирование)"""
    
    def __init__(self, duration: int = 2000):
        super().__init__(duration)
        self.cycle_duration = duration
    
    def get_scale(self, elapsed: int) -> float:
        """
        Возвращает масштаб для текущего времени.
        
        Returns:
            Значение от 1.0 до 1.2 (пульсация)
        """
        progress = (elapsed % self.cycle_duration) / self.cycle_duration
        # Синусоида для плавной пульсации
        return 1.0 + 0.1 * math.sin(progress * 2 * math.pi)


class ShakeAnimation(Animation):
    """Анимация встряхивания (для ошибок)"""
    
    def __init__(self, amplitude: int = 10, duration: int = 400):
        super().__init__(duration)
        self.amplitude = amplitude
    
    def get_offset_x(self, elapsed: int) -> int:
        """Возвращает смещение по X для эффекта встряхивания"""
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            return 0
        
        # Затухающие колебания
        shake = self.amplitude * (1 - progress) * math.sin(progress * 10 * math.pi)
        return int(shake)


class ParticleEffect:
    """Эффект частиц (конфетти)"""
    
    def __init__(self, canvas: tk.Canvas, x: int, y: int, count: int = 20):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.particles = []
        
        # Создаем частицы
        colors = [Colors.SUCCESS, Colors.PRIMARY, Colors.WARNING, Colors.DANGER, "#feca57", "#48dbfb"]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            color = random.choice(colors)
            size = random.randint(3, 8)
            
            particle = {
                'id': canvas.create_oval(x, y, x + size, y + size, fill=color, outline=""),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 5,  # Начальная скорость вверх
                'life': 1.0,
                'size': size
            }
            self.particles.append(particle)
    
    def update(self, elapsed: int) -> bool:
        """Обновляет позиции частиц"""
        gravity = 0.3
        all_done = True
        
        for particle in self.particles:
            if particle['life'] <= 0:
                continue
            
            all_done = False
            
            # Физика
            particle['vy'] += gravity
            
            # Обновляем позицию
            coords = self.canvas.coords(particle['id'])
            if len(coords) == 4:
                x1, y1, x2, y2 = coords
                new_x1 = x1 + particle['vx']
                new_y1 = y1 + particle['vy']
                new_x2 = x2 + particle['vx']
                new_y2 = y2 + particle['vy']
                
                self.canvas.coords(particle['id'], new_x1, new_y1, new_x2, new_y2)
            
            # Уменьшаем время жизни
            particle['life'] -= 0.02
            
            if particle['life'] <= 0:
                self.canvas.delete(particle['id'])
        
        return all_done


class AnimationManager:
    """Менеджер анимаций"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.animations = []
        self.running = False
        self.start_time = None
    
    def add(self, animation: Animation):
        """Добавляет анимацию в очередь"""
        self.animations.append(animation)
        if not self.running:
            self.start()
    
    def start(self):
        """Запускает цикл анимаций"""
        self.running = True
        self.start_time = self.root.tk.call('clock', 'milliseconds')
        self.update()
    
    def update(self):
        """Обновляет все активные анимации"""
        if not self.running or not self.animations:
            self.running = False
            return
        
        current_time = self.root.tk.call('clock', 'milliseconds')
        elapsed = current_time - self.start_time
        
        # Обновляем все анимации
        self.animations = [anim for anim in self.animations 
                          if not anim.update(elapsed)]
        
        # Продолжаем цикл если есть активные анимации
        if self.animations:
            self.root.after(16, self.update)  # ~60 FPS
        else:
            self.running = False
    
    def clear(self):
        """Останавливает все анимации"""
        self.animations.clear()
        self.running = False


# Импортируем random для ParticleEffect
import random


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def ease_in_out_cubic(t: float) -> float:
    """Кубическая функция замедления (плавный старт и конец)"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - math.pow(-2 * t + 2, 3) / 2


def ease_out_bounce(t: float) -> float:
    """Эффект отскока"""
    n1 = 7.5625
    d1 = 2.75
    
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def create_float_text(canvas: tk.Canvas, x: int, y: int, text: str, 
                     color: str = Colors.SUCCESS, duration: int = 1000):
    """
    Создает всплывающий текст с анимацией.
    
    Args:
        canvas: Canvas для отображения
        x, y: Начальная позиция
        text: Текст для отображения
        color: Цвет текста
        duration: Длительность анимации
    """
    text_id = canvas.create_text(x, y, text=text, font=Fonts.SCORE, 
                                 fill=color, anchor="center")
    
    def animate_step(step: int, max_steps: int):
        if step >= max_steps:
            canvas.delete(text_id)
            return
        
        progress = step / max_steps
        offset_y = -60 * ease_in_out_cubic(progress)
        
        # Fade out в конце
        if progress > 0.7:
            alpha = int(255 * (1 - (progress - 0.7) / 0.3))
            # Tkinter не поддерживает альфа-канал, поэтому просто удаляем в конце
            if progress > 0.95:
                canvas.itemconfig(text_id, fill=color + "80")
        
        canvas.coords(text_id, x, y + offset_y)
        canvas.after(duration // max_steps, lambda: animate_step(step + 1, max_steps))
    
    animate_step(0, 30)


def create_shake_effect(widget: tk.Widget, amplitude: int = 10, duration: int = 400):
    """
    Создает эффект встряхивания виджета.
    
    Args:
        widget: Виджет для встряхивания
        amplitude: Амплитуда встряхивания
        duration: Длительность
    """
    original_x = widget.winfo_x()
    original_y = widget.winfo_y()
    
    def shake_step(step: int, max_steps: int):
        if step >= max_steps:
            widget.place(x=original_x, y=original_y)
            return
        
        progress = step / max_steps
        shake = amplitude * (1 - progress) * math.sin(progress * 10 * math.pi)
        
        widget.place(x=original_x + int(shake), y=original_y)
        widget.after(duration // max_steps, lambda: shake_step(step + 1, max_steps))
    
    shake_step(0, 20)
