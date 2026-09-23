import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../../src/components/chat/ChatInput';

describe('ChatInput', () => {
  it('renderiza el textarea y el botón de envío', () => {
    render(<ChatInput onSendMessage={vi.fn()} disabled={false} />);
    
    expect(screen.getByPlaceholderText(/Escribe un mensaje/i)).toBeDefined();
    expect(screen.getByRole('button')).toBeDefined();
  });

  it('llama a onSendMessage con el texto correcto al presionar Enter', () => {
    const mockOnSendMessage = vi.fn();
    render(<ChatInput onSendMessage={mockOnSendMessage} disabled={false} />);
    
    const textarea = screen.getByPlaceholderText(/Escribe un mensaje/i);
    
    // Simular escritura
    fireEvent.change(textarea, { target: { value: 'Hola bot' } });
    
    // Simular pulsación de Enter (sin Shift)
    fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter', shiftKey: false });
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Hola bot');
    expect(mockOnSendMessage).toHaveBeenCalledTimes(1);
  });

  it('no envía el mensaje si está vacío o solo contiene espacios', () => {
    const mockOnSendMessage = vi.fn();
    render(<ChatInput onSendMessage={mockOnSendMessage} disabled={false} />);
    
    const textarea = screen.getByPlaceholderText(/Escribe un mensaje/i);
    
    // Simular escritura de espacios
    fireEvent.change(textarea, { target: { value: '   ' } });
    
    const button = screen.getByRole('button');
    expect(button.hasAttribute('disabled')).toBeTruthy();
    
    fireEvent.click(button);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('deshabilita el input y el botón cuando la prop disabled es true', () => {
    render(<ChatInput onSendMessage={vi.fn()} disabled={true} />);
    
    const textarea = screen.getByPlaceholderText(/Escribe un mensaje/i);
    const button = screen.getByRole('button');
    
    expect(textarea.hasAttribute('disabled')).toBeTruthy();
    expect(button.hasAttribute('disabled')).toBeTruthy();
  });
});