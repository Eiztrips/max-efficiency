import axios from 'axios';

const API_BASE_URL = '/api/v1';

class ApiService {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    //FIXME: Для прода кидать на апи в заголовке строку initData для аунтефикации
    // https://dev.max.ru/docs/webapps/validation
    // Не успею сделать да простят нас

    try {
      const res = await axios({
        url,
        method: options.method || 'GET',
        headers: options.headers,
        data: options.body,
        params: options.params,
      });
      
      return res.data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // ============ User Methods ============

  /**
   * Получить пользователя по max_user_id
   * @param {number} maxUserId - ID пользователя из MAX
   */
  getUserProfile(maxUserId) {
    return this.request(`/users/${maxUserId}`);
  }

  /**
   * Создать или получить существующего пользователя
   * @param {Object} userData - {max_user_id: number, username?: string}
   */
  createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: userData,
    });
  }

  /**
   * Получить все категории пользователя
   * @param {number} maxUserId - ID пользователя
   */
  getUserCategories(maxUserId) {
    return this.request(`/users/${maxUserId}/categories`);
  }

  /**
   * Получить все теги пользователя
   * @param {number} maxUserId - ID пользователя
   */
  getUserTags(maxUserId) {
    return this.request(`/users/${maxUserId}/tags`);
  }

  /**
   * Получить все задачи пользователя
   * @param {number} maxUserId - ID пользователя
   */
  getUserTasks(maxUserId) {
    return this.request(`/users/${maxUserId}/tasks`);
  }

  // ============ Category Methods ============
  
  /**
   * Получить все категории (DEBUG)
   */
  getCategories() {
    return this.request('/categories/debug');
  }

  /**
   * Получить категорию по ID
   * @param {number} id - ID категории
   */
  getCategory(id) {
    return this.request(`/categories/${id}`);
  }

  /**
   * Создать новую категорию
   * @param {Object} categoryData - {max_user_id: number, name: string, description?: string}
   */
  createCategory(categoryData) {
    return this.request('/categories', {
      method: 'POST',
      body: categoryData,
    });
  }

  /**
   * Удалить категорию по ID
   * @param {number} id - ID категории
   */
  deleteCategory(id) {
    return this.request(`/categories/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Получить всех пользователей категории
   * @param {number} id - ID категории
   */
  getCategoryUsers(id) {
    return this.request(`/categories/${id}/users`);
  }

  /**
   * Получить все теги категории
   * @param {number} id - ID категории
   */
  getCategoryTags(id) {
    return this.request(`/categories/${id}/tags`);
  }

  /**
   * Получить все задачи категории
   * @param {number} id - ID категории
   */
  getCategoryTasks(id) {
    return this.request(`/categories/${id}/tasks`);
  }

  /**
   * Добавить пользователя в категорию
   * @param {number} categoryId - ID категории
   * @param {number} maxUserId - ID пользователя
   * @param {Object} data - {id: categoryId, max_user_id: maxUserId}
   */
  addUserToCategory(categoryId, maxUserId, data) {
    return this.request(`/categories/${categoryId}/users/${maxUserId}`, {
      method: 'POST',
      body: data,
    });
  }

  /**
   * Удалить пользователя из категории
   * @param {number} categoryId - ID категории
   * @param {number} maxUserId - ID пользователя
   */
  removeUserFromCategory(categoryId, maxUserId) {
    return this.request(`/categories/${categoryId}/users/${maxUserId}`, {
      method: 'DELETE',
    });
  }

  // ============ Task Methods ============
  
  /**
   * Получить все задачи (DEBUG)
   */
  getAllTasks() {
    return this.request('/tasks/debug');
  }

  /**
   * Получить задачи с фильтрацией
   * @param {Object} filters - {
   *   max_user_id: number (required),
   *   category_id?: number,
   *   tag_id?: number,
   *   status?: string,
   *   is_completed?: boolean,
   *   from_date?: string (ISO format),
   *   to_date?: string (ISO format),
   *   search?: string
   * }
   */
  getTasks(filters) {
    return this.request('/tasks', {
      params: filters,
    });
  }

  /**
   * Получить задачу по ID
   * @param {number} id - ID задачи
   */
  getTask(id) {
    return this.request(`/tasks/${id}`);
  }

  /**
   * Сгенерировать задачу через AI
   * @param {Object} taskData - {max_user_id: number, prompt: string, category_id: number}
   */
  generateTask(taskData) {
    return this.request('/tasks/generate', {
      method: 'POST',
      body: taskData,
    });
  }

  /**
   * Создать задачу вручную
   * @param {Object} taskData - {max_user_id: number, title: string, description?: string, category_id: number, expiration_date?: string}
   */
  createTask(taskData) {
    return this.request('/tasks', {
      method: 'POST',
      body: taskData,
    });
  }

  /**
   * Обновить задачу по ID
   * @param {number} id - ID задачи
   * @param {Object} data - Данные для обновления
   */
  updateTask(id, data) {
    return this.request(`/tasks/${id}`, {
      method: 'PATCH',
      body: data,
    });
  }

  /**
   * Обновить теги задачи (заменить все теги)
   * @param {number} taskId - ID задачи
   * @param {number[]} tagIds - Массив ID тегов
   */
  updateTaskTags(taskId, tagIds) {
    return this.request(`/tasks/${taskId}/tags`, {
      method: 'PUT',
      body: tagIds,
    });
  }

  /**
   * Добавить тег к задаче
   * @param {number} taskId - ID задачи
   * @param {number} tagId - ID тега
   */
  addTagToTask(taskId, tagId) {
    return this.request(`/tasks/${taskId}/tags/${tagId}`, {
      method: 'POST',
    });
  }

  /**
   * Удалить тег из задачи
   * @param {number} taskId - ID задачи
   * @param {number} tagId - ID тега
   */
  removeTagFromTask(taskId, tagId) {
    return this.request(`/tasks/${taskId}/tags/${tagId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Удалить задачу по ID
   * @param {number} id - ID задачи
   */
  deleteTask(id) {
    return this.request(`/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  // ============ Tag Methods ============
  
  /**
   * Получить все теги (DEBUG)
   */
  getAllTags() {
    return this.request('/tags/debug');
  }

  /**
   * Получить тег по ID
   * @param {number} id - ID тега
   */
  getTag(id) {
    return this.request(`/tags/${id}`);
  }

  /**
   * Создать новый тег
   * @param {Object} tagData - {category_id: number, name: string, color?: string}
   */
  createTag(tagData) {
    return this.request('/tags', {
      method: 'POST',
      body: tagData,
    });
  }

  /**
   * Удалить тег по ID
   * @param {number} id - ID тега
   */
  deleteTag(id) {
    return this.request(`/tags/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Получить все задачи с данным тегом
   * @param {number} id - ID тега
   */
  getTagTasks(id) {
    return this.request(`/tags/${id}/tasks`);
  }
}

const apiService = new ApiService();
export default apiService;
