import { setAuth } from '../utils/auth';
import { BACKEND } from '../constants';
import { checkAuth } from './ProtectedRoute'

// Mock react-router
jest.mock('react-router', () => ({
  Navigate: jest.fn(),
  useLocation: jest.fn(),
}));

// Mock the auth module
jest.mock('../utils/auth', () => ({
  setAuth: jest.fn(),
  getAuthToken: jest.fn(),
}));

jest.mock('../constants', () => ({
  BACKEND: 'http://test-backend.com',
}));

describe('checkAuth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    delete global.fetch;
  });

  describe('when user is not authenticated', () => {
    it('redirects to login when accessing protected route without token', async () => {
      const result = await checkAuth('/dashboard', null, false);

      expect(result).toEqual({
        msg: null,
        path: '/login'
      });
    });

    it('does not redirect when already on login page without token', async () => {
      const result = await checkAuth('/login', null, false);

      expect(result).toEqual({auth: false});
    });
  });

  describe('when user is authenticated', () => {
    it('redirects to home when accessing login page with valid token', async () => {
      const result = await checkAuth('/login', 'valid-token', false);

      expect(result).toEqual({
        msg: null,
        path: '/'
      });
    });

    it('allows access to protected route with valid token and valid user', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ admin: false, name: 'Test User' })
      });

      const result = await checkAuth('/dashboard', 'valid-token', false);

      expect(result).toEqual({ auth: true });
      expect(global.fetch).toHaveBeenCalledWith(
        'http://test-backend.com/users/current',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer valid-token'
          }
        }
      );
    });

    it('clears auth and redirects to login when token is invalid', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 401
      });

      const result = await checkAuth('/dashboard', 'invalid-token', false);

      expect(result).toEqual({
        msg: 'Unauthorized. Please log in again.',
        path: '/login'
      });
      expect(setAuth).toHaveBeenCalledWith(null);
    });
  });

  describe('when route requires admin access', () => {
    it('allows access for admin user on admin route', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ admin: true, name: 'Admin User' })
      });

      const result = await checkAuth('/admin', 'admin-token', true);

      expect(result).toEqual({ auth: true });
    });

    it('redirects non-admin user to home when accessing admin route', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ admin: false, name: 'Regular User' })
      });

      const result = await checkAuth('/admin', 'user-token', true);

      expect(result).toEqual({
        msg: 'Unauthorized. You are not an admin',
        path: '/'
      });
    });

    it('allows non-admin user on non-admin route', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ admin: false, name: 'Regular User' })
      });

      const result = await checkAuth('/dashboard', 'user-token', false);

      expect(result).toEqual({ auth: true });
    });
  });

  describe('edge cases', () => {
    it('handles fetch errors gracefully', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'));

      await expect(checkAuth('/dashboard', 'token', false)).rejects.toThrow('Network error');
    });

    it('handles malformed JSON response', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      await expect(checkAuth('/dashboard', 'token', false)).rejects.toThrow('Invalid JSON');
    });
  });
});
