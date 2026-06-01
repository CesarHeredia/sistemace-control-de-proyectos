// ============ DATA ============
let students = [];

let currentUser = null;
let currentLevel = 'primaria';
let currentTab = 'inicio';

const levelNames = { primaria: 'Primaria', prescolar: 'Preescolar', bachillerato: 'Bachillerato' };

// ============ DOM REFS ============
const $ = id => document.getElementById(id);
const loginScreen = $('loginScreen');
const dashboardScreen = $('dashboardScreen');
const loginForm = $('loginForm');
const registerForm = $('registerForm');
const loginError = $('loginError');
const registerError = $('registerError');
const registerSuccess = $('registerSuccess');
const searchInput = $('searchInput');
const studentsBody = $('studentsTableBody');
const searchBody = $('searchResultsBody');
const searchEmpty = $('searchEmpty');
const studentsEmpty = $('studentsEmpty');
const levelsBody = $('levelsTableBody');
const levelsEmpty = $('levelsEmpty');
const resultCount = $('resultCount');
const currentLevelSpan = $('currentLevel');
const dashboardTitle = $('dashboardTitle');
const modal = $('addStudentModal');
const studentForm = $('studentForm');
const hamburger = $('hamburger');
const sidebar = $('sidebar');

// ============ AUTH TABS ============
document.querySelectorAll('.auth-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    tab.classList.add('active');
    $(tab.dataset.form + 'Form').classList.add('active');
    loginError.classList.remove('show');
    registerError.classList.remove('show');
    registerSuccess.classList.remove('show');
  });
});

// ============ LOGIN ============
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = $('username').value.trim();
  const password = $('password').value.trim();

  const response = await eel.login(username, password)();
  
  if (response.success) {
    currentUser = response.user;
    loginSuccess();
  } else {
    loginError.textContent = response.error || 'Usuario o contraseña incorrectos';
    loginError.classList.add('show');
  }
});

function loginSuccess() {
  loginError.classList.remove('show');
  currentLevel = currentUser.isAdmin ? 'primaria' : currentUser.level;
  showScreen('dashboard');
  currentTab = 'inicio';
  updateSidebarUser();
  applyPermissions();
  renderDashboard();
}

// ============ REGISTER ============
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = $('regUser').value.trim();
  const password = $('regPass').value.trim();
  const confirm = $('regPassConfirm').value.trim();
  const level = $('regLevel').value;

  registerError.classList.remove('show');
  registerSuccess.classList.remove('show');

  if (!username || !password || !confirm) {
    registerError.textContent = 'Completa todos los campos';
    registerError.classList.add('show');
    return;
  }

  if (password !== confirm) {
    registerError.textContent = 'Las contraseñas no coinciden';
    registerError.classList.add('show');
    return;
  }

  if (password.length < 4) {
    registerError.textContent = 'La contraseña debe tener al menos 4 caracteres';
    registerError.classList.add('show');
    return;
  }

  const response = await eel.register(username, password, level)();

  if (response.success) {
    registerForm.reset();
    registerSuccess.classList.add('show');
    setTimeout(() => {
      registerSuccess.classList.remove('show');
      document.querySelector('.auth-tab[data-form="login"]').click();
      $('username').value = username;
      $('password').value = password;
    }, 1500);
  } else {
    registerError.textContent = response.error || 'Error al registrar';
    registerError.classList.add('show');
  }
});

// ============ SCREEN NAV ============
function showScreen(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  if (screen === 'login') loginScreen.classList.add('active');
  if (screen === 'dashboard') dashboardScreen.classList.add('active');
}

// ============ SIDEBAR USER ============
function updateSidebarUser() {
  $('sidebarUserName').textContent = currentUser.username;
  $('sidebarUserLevel').textContent = currentUser.isAdmin
    ? 'Administrador'
    : levelNames[currentUser.level];
}

function applyPermissions() {
  const isAdmin = currentUser.isAdmin;
  const userLvl = currentUser.level;

  // Ocultar pestaña "Niveles" si no es admin
  const nivelesNav = document.querySelector('.nav-item[data-tab="niveles"]');
  if (nivelesNav) {
    nivelesNav.style.display = isAdmin ? 'flex' : 'none';
  }

  // Filtrar botones de acceso rápido
  document.querySelectorAll('.welcome-level-btn').forEach(btn => {
    if (!isAdmin && btn.dataset.level !== userLvl) {
      btn.style.display = 'none';
    } else {
      btn.style.display = 'inline-flex';
    }
  });

  // Filtrar tarjetas de estadísticas
  ['primaria', 'prescolar', 'bachillerato'].forEach(lvl => {
    const statCount = document.getElementById('count-' + lvl);
    if (statCount) {
      const card = statCount.closest('.stat-card');
      if (card) {
        if (!isAdmin && lvl !== userLvl) {
          card.style.display = 'none';
        } else {
          card.style.display = 'flex';
        }
      }
    }
  });

  // Bloquear el selector de nivel al agregar un alumno
  const sLevel = $('sLevel');
  if (sLevel) {
    if (!isAdmin) {
      sLevel.value = userLvl;
      sLevel.disabled = true;
    } else {
      sLevel.disabled = false;
    }
  }
}

// ============ DASHBOARD ============
async function renderDashboard() {
  currentLevelSpan.textContent = levelNames[currentLevel];
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const tabEl = document.getElementById('tab-' + currentTab);
  if (tabEl) tabEl.classList.add('active');

  const navEl = document.querySelector(`.nav-item[data-tab="${currentTab}"]`);
  if (navEl) navEl.classList.add('active');

  dashboardTitle.textContent = currentTab === 'inicio' ? 'Inicio' : currentTab === 'alumnos' ? 'Alumnos' : 'Niveles';

  students = await eel.get_alumnos(null)();

  updateCounts();
  renderStudents();
  renderLevelsTable();
  handleSearch();

  document.querySelectorAll('.level-tab').forEach(t => t.classList.remove('active'));
  const activeLevelTab = document.querySelector(`.level-tab[data-level="${currentLevel}"]`);
  if (activeLevelTab) activeLevelTab.classList.add('active');
}

function updateCounts() {
  ['primaria', 'prescolar', 'bachillerato'].forEach(level => {
    const count = students.filter(s => s.level === level).length;
    const el = document.getElementById('count-' + level);
    if (el) el.textContent = count;
  });
}

// ============ WELCOME LEVEL BTNS ============
document.querySelectorAll('.welcome-level-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    currentLevel = btn.dataset.level;
    currentTab = 'alumnos';
    renderDashboard();
  });
});

// ============ STUDENTS TABLE ============
function renderStudents() {
  const q = searchInput.value.trim().toLowerCase();
  const filtered = students.filter(s => 
    s.level === currentLevel &&
    (!q || s.nombre.toLowerCase().includes(q) || s.apellido.toLowerCase().includes(q) || s.cedula.toLowerCase().includes(q) || (s.anios && s.anios.some(a => a.toLowerCase().includes(q))))
  );

  if (filtered.length === 0) {
    studentsBody.innerHTML = '';
    studentsEmpty.style.display = 'block';
    return;
  }
  studentsEmpty.style.display = 'none';
  studentsBody.innerHTML = filtered.map(s => `
    <tr>
      <td><strong>${s.nombre}</strong></td>
      <td>${s.apellido}</td>
      <td>${levelNames[s.level]}</td>
      <td>${s.cedula}</td>
      <td>
        <button onclick="openPerfil(${s.id})" style="background:none;border:none;cursor:pointer;color:#4f46e5;font-size:1.2rem;" title="Ver perfil"><i class="fas fa-eye"></i></button>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('#studentsTableBody .btn-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteStudent(btn.dataset.id));
  });
}

// ============ SEARCH ============
function handleSearch() {
  const q = searchInput.value.trim().toLowerCase();

  if (!q) {
    searchBody.innerHTML = '';
    searchEmpty.style.display = 'block';
    searchEmpty.querySelector('p').textContent = 'Busca alumnos por nombre, apellido o matrícula';
    resultCount.textContent = '0 alumnos';
  } else {
    const results = students.filter(s =>
      s.nombre.toLowerCase().includes(q) ||
      s.apellido.toLowerCase().includes(q) ||
      s.cedula.toLowerCase().includes(q) ||
      (s.anios && s.anios.some(a => a.toLowerCase().includes(q)))
    );

    resultCount.textContent = `${results.length} alumno${results.length !== 1 ? 's' : ''}`;

    if (results.length === 0) {
      searchBody.innerHTML = '';
      searchEmpty.style.display = 'block';
      searchEmpty.querySelector('p').textContent = 'No se encontraron alumnos';
    } else {
      searchEmpty.style.display = 'none';
      searchBody.innerHTML = results.map(s => `
        <tr>
          <td><strong>${s.nombre}</strong></td>
          <td>${s.apellido}</td>
          <td>${levelNames[s.level]}</td>
          <td>${s.cedula}</td>
          <td>
            <button onclick="openPerfil(${s.id})" style="background:none;border:none;cursor:pointer;color:#4f46e5;font-size:1.2rem;" title="Ver perfil"><i class="fas fa-eye"></i></button>
          </td>
        </tr>
      `).join('');
    }
  }

  // Aplicar también a las otras tablas
  renderStudents();
  renderLevelsTable();
}

searchInput.addEventListener('input', handleSearch);

// ============ LEVELS TABLE ============
function renderLevelsTable() {
  const q = searchInput.value.trim().toLowerCase();
  const filtered = students.filter(s => 
    s.level === currentLevel &&
    (!q || s.nombre.toLowerCase().includes(q) || s.apellido.toLowerCase().includes(q) || s.cedula.toLowerCase().includes(q) || (s.anios && s.anios.some(a => a.toLowerCase().includes(q))))
  );

  if (filtered.length === 0) {
    levelsBody.innerHTML = '';
    levelsEmpty.style.display = 'block';
    return;
  }
  levelsEmpty.style.display = 'none';
  levelsBody.innerHTML = filtered.map(s => `
    <tr>
      <td><strong>${s.nombre}</strong></td>
      <td>${s.apellido}</td>
      <td>${s.cedula}</td>
      <td>
        <button onclick="openPerfil(${s.id})" style="background:none;border:none;cursor:pointer;color:#4f46e5;font-size:1.2rem;" title="Ver perfil"><i class="fas fa-eye"></i></button>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('#levelsTableBody .btn-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteStudent(btn.dataset.id));
  });
}

document.querySelectorAll('.level-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.level-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentLevel = tab.dataset.level;
    currentLevelSpan.textContent = levelNames[currentLevel];
    renderLevelsTable();
  });
});

// ============ NAVIGATION ============
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    currentTab = item.dataset.tab;
    if (currentTab === 'inicio') {
      currentLevelSpan.textContent = levelNames[currentLevel];
    }
    renderDashboard();
    if (window.innerWidth <= 768) sidebar.classList.remove('open');
  });
});

// ============ LOGOUT ============
$('logoutBtn').addEventListener('click', () => {
  currentUser = null;
  showScreen('login');
  $('username').value = '';
  $('password').value = '';
  loginError.classList.remove('show');
  document.querySelector('.auth-tab[data-form="login"]').click();
});

// ============ MODAL ============
$('addStudentBtn').addEventListener('click', () => {
  modal.classList.add('show');
  studentForm.reset();
  $('sLevel').value = currentLevel;
  $('sId').value = '';
  $('sTipo').value = 'Regular';
  $('sIngresoPeriodoGroup').style.display = 'none';
  populateIngresoPeriodoDropdown();
  renderNotasModal(currentLevel);
});

// Re-render notes when level changes inside the modal
$('sLevel').addEventListener('change', function() {
  populateIngresoPeriodoDropdown();
  renderNotasModal(this.value);
});

// Handle type changes inside the modal
$('sTipo').addEventListener('change', function() {
  if (this.value === 'Nuevo Ingreso') {
    $('sIngresoPeriodoGroup').style.display = 'block';
    populateIngresoPeriodoDropdown();
  } else {
    $('sIngresoPeriodoGroup').style.display = 'none';
  }
  renderNotasModal($('sLevel').value);
});

$('sIngresoPeriodo').addEventListener('change', function() {
  renderNotasModal($('sLevel').value);
});

function populateIngresoPeriodoDropdown() {
  const nivel = $('sLevel').value;
  const dropdown = $('sIngresoPeriodo');
  const perList = periodos[nivel] || [];
  dropdown.innerHTML = perList.map(p => `<option value="${p}">${p}</option>`).join('');
}

function renderNotasModal(nivel) {
  const grid = $('notasFilesGrid');
  const tipo = $('sTipo').value;
  const ingresoPeriodo = $('sIngresoPeriodo').value;
  const perList = periodos[nivel] || [];
  grid.innerHTML = '';
  
  // Decide which periods to display
  let periodsToShow = [];
  if (tipo === 'Egresado') {
    periodsToShow = ['Notas Totales'];
  } else if (tipo === 'Nuevo Ingreso') {
    const idx = perList.indexOf(ingresoPeriodo);
    if (idx > 0) {
      periodsToShow = ['Notas del Colegio Anterior'];
    } else {
      periodsToShow = [];
    }
  } else {
    periodsToShow = perList;
  }
  
  if (periodsToShow.length === 0) {
    grid.innerHTML = `
      <div style="padding:15px;text-align:center;color:#6b7280;background:#f3f4f6;border-radius:10px;font-size:0.9rem;">
        No hay notas de años anteriores para adjuntar en este nivel de ingreso.
      </div>`;
    return;
  }
  
  periodsToShow.forEach(p => {
    const safeId = 'addfile_' + p.replace(/[^a-zA-Z0-9]/g, '_');
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;';
    row.innerHTML = `
      <span style="font-weight:500;color:#374151;font-size:0.9rem;">${p}</span>
      <div style="display:flex;align-items:center;gap:10px;">
        <input type="text" id="${safeId}_anio" placeholder="Año (ej. 2023)" style="width:100px;padding:4px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:0.85rem;" value="${new Date().getFullYear()}">
        <label for="${safeId}" style="display:inline-flex;align-items:center;gap:6px;cursor:pointer;">
          <input type="file" id="${safeId}" data-periodo="${p}" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" style="display:none;">
          <span id="${safeId}_label" style="font-size:0.82rem;color:#6b7280;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">Sin archivo</span>
          <span style="background:#4f46e5;color:white;border:none;padding:5px 12px;border-radius:7px;font-size:0.8rem;">
            <i class="fas fa-paperclip"></i> Adjuntar
          </span>
        </label>
      </div>
    `;
    
    // Update label text when file picked
    const inputEl = row.querySelector(`#${safeId}`);
    inputEl.addEventListener('change', function() {
      const lbl = $(`${safeId}_label`);
      if (this.files[0]) {
        lbl.textContent = this.files[0].name;
        lbl.style.color = '#10b981';
      } else {
        lbl.textContent = 'Sin archivo';
        lbl.style.color = '#6b7280';
      }
    });
    grid.appendChild(row);
  });
}

$('closeModal').addEventListener('click', () => modal.classList.remove('show'));
$('cancelModalBtn').addEventListener('click', () => modal.classList.remove('show'));
modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('show'); });

studentForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const newStudent = {
    cedula: $('sId').value.trim(),
    nombre: $('sName').value.trim(),
    apellido: $('sLastName').value.trim(),
    nivel: $('sLevel').value
  };

  if (!newStudent.nombre || !newStudent.apellido || !newStudent.cedula) return;

  const tipo = $('sTipo').value;
  const ingreso_periodo = (tipo === 'Nuevo Ingreso') ? $('sIngresoPeriodo').value : null;

  // Collect files before saving (FileReader must run in sync context)
  const fileInputs = $('notasFilesGrid').querySelectorAll('input[type="file"]');
  const filesToUpload = [];
  for (const inp of fileInputs) {
    if (inp.files[0]) {
      const anioInput = document.getElementById(inp.id + '_anio');
      const anio = anioInput ? anioInput.value.trim() : '';
      filesToUpload.push({ periodo: inp.dataset.periodo, file: inp.files[0], anio: anio || new Date().getFullYear().toString() });
    }
  }

  // Disable button while saving
  const saveBtn = $('saveStudentBtn');
  saveBtn.disabled = true;
  saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';

  const response = await eel.add_alumno(newStudent.cedula, newStudent.nombre, newStudent.apellido, newStudent.nivel, tipo, ingreso_periodo)();

  if (!response.success) {
    saveBtn.disabled = false;
    saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar Alumno';
    alert(response.error);
    return;
  }

  // Upload files if any
  if (filesToUpload.length > 0) {
    // Reload to get new student's id
    const updatedStudents = await eel.get_alumnos(null)();
    const saved = updatedStudents.find(s => s.cedula === newStudent.cedula);
    if (saved) {
      for (const item of filesToUpload) {
        await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = async function() {
            await eel.upload_nota(saved.id, item.periodo, reader.result, item.file.name, item.anio)();
            resolve();
          };
          reader.readAsDataURL(item.file);
        });
      }
    }
  }

  saveBtn.disabled = false;
  saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar Alumno';
  modal.classList.remove('show');
  renderDashboard();
});

// ============ DELETE ============
async function deleteStudent(id) {
  if (!confirm('¿Eliminar este alumno y todos sus archivos?')) return;
  const res = await eel.delete_alumno(parseInt(id))();
  if(res.success) {
    renderDashboard();
  } else {
    alert("Error al eliminar: " + res.error);
  }
}

// ============ PERFIL MODAL ============
const perfilModal = $('perfilModal');
const closePerfilModal = $('closePerfilModal');
perfilModal.addEventListener('click', (e) => { if (e.target === perfilModal) perfilModal.classList.remove('show'); });
closePerfilModal.addEventListener('click', () => perfilModal.classList.remove('show'));

const periodos = {
  'primaria': ['1er Grado', '2do Grado', '3er Grado', '4to Grado', '5to Grado', '6to Grado'],
  'prescolar': ['2do Nivel', '3er Nivel'],
  'bachillerato': ['1er A\u00f1o', '2do A\u00f1o', '3er A\u00f1o', '4to A\u00f1o', '5to A\u00f1o']
};

let perfilAlumnoActual = null;

async function openPerfil(alumnoId) {
  const alumno = students.find(s => s.id === alumnoId);
  if (!alumno) return;
  
  perfilAlumnoActual = alumno;
  
  // Llenar datos del perfil
  $('perfilNombreCompleto').textContent = alumno.nombre + ' ' + alumno.apellido;
  $('perfilCedula').textContent = alumno.cedula;
  $('perfilNivel').textContent = levelNames[alumno.level];
  $('perfilTipo').textContent = alumno.tipo === 'Nuevo Ingreso' 
    ? `Nuevo Ingreso (${alumno.ingreso_periodo})` 
    : (alumno.tipo || 'Regular');
  
  perfilModal.classList.add('show');
  
  // Cargar notas
  const notasContainer = $('perfilNotas');
  notasContainer.innerHTML = '<p style="color:#6b7280;"><i class="fas fa-spinner fa-spin"></i> Cargando archivos...</p>';
  
  const res = await eel.get_notas(alumnoId)();
  const notasSubidas = res.success ? res.notas : {};
  
  // Determinar la lista de periodos
  let perList = [];
  let entryIdx = -1;
  
  if (alumno.tipo === 'Egresado') {
    perList = ['Notas Totales'];
  } else if (alumno.tipo === 'Nuevo Ingreso') {
    const fullList = periodos[alumno.level] || [];
    entryIdx = fullList.indexOf(alumno.ingreso_periodo);
    if (entryIdx > 0) {
      perList = ['Notas del Colegio Anterior', ...fullList.slice(entryIdx)];
    } else {
      perList = fullList;
    }
  } else {
    perList = periodos[alumno.level] || [];
  }
  
  notasContainer.innerHTML = '';
  let hasAnyNote = false;
  for (let i = 0; i < perList.length; i++) {
    const p = perList[i];
    const notaInfo = notasSubidas[p];
    const tieneNota = !!notaInfo;
    if (tieneNota) hasAnyNote = true;
    const nombreArchivo = tieneNota ? notaInfo.archivo : null;
    const anio = tieneNota && notaInfo.anio ? ` (Año: ${notaInfo.anio})` : '';

    let labelPrefix = '';
    let badge = '';
    
    if (p === 'Notas del Colegio Anterior') {
      labelPrefix = ' <span style="background:#6b7280;color:white;padding:2px 6px;border-radius:4px;font-size:0.75rem;margin-left:8px;font-weight:normal;">Col. Anterior</span>';
      badge = tieneNota
        ? `<span style="color:#10b981;font-size:0.85em;"><i class="fas fa-check-circle"></i> ${nombreArchivo}${anio}</span>`
        : '<span style="color:#9ca3af;font-size:0.85em;"><i class="fas fa-times-circle"></i> Sin archivo (Colegio Anterior)</span>';
    } else if (alumno.tipo === 'Nuevo Ingreso' && p !== 'Notas del Colegio Anterior') {
      labelPrefix = ' <span style="background:#4f46e5;color:white;padding:2px 6px;border-radius:4px;font-size:0.75rem;margin-left:8px;font-weight:normal;">En el colegio</span>';
      badge = tieneNota
        ? `<span style="color:#10b981;font-size:0.85em;"><i class="fas fa-check-circle"></i> ${nombreArchivo}${anio}</span>`
        : '<span style="color:#ef4444;font-size:0.85em;"><i class="fas fa-exclamation-circle"></i> Falta por ver en el colegio</span>';
    } else {
      badge = tieneNota
        ? `<span style="color:#10b981;font-size:0.85em;"><i class="fas fa-check-circle"></i> ${nombreArchivo}${anio}</span>`
        : '<span style="color:#9ca3af;font-size:0.85em;"><i class="fas fa-times-circle"></i> Sin archivo</span>';
    }
    
    const verBtn = tieneNota
      ? `<button onclick="verArchivo(${alumnoId}, '${p}')" style="background:#10b981;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;">
           <i class="fas fa-eye"></i> Ver
         </button>`
      : '';

    const row = document.createElement('div');
    row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;';
    row.innerHTML = `
      <div>
        <span style="font-weight:600;color:#374151;">${p}${labelPrefix}</span><br>
        <small>${badge}</small>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        ${verBtn}
        <input type="text" id="panio_${alumnoId}_${p.replace(/[^a-zA-Z0-9]/g, '_')}" data-periodo="${p}" placeholder="Año" style="width:70px;padding:4px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:0.85rem;" value="${tieneNota && notaInfo.anio ? notaInfo.anio : new Date().getFullYear()}" disabled class="anio-input">
        <input type="file" id="pfile_${alumnoId}_${p.replace(/[^a-zA-Z0-9]/g, '_')}" style="display:none;" onchange="uploadFileFromPerfil(${alumnoId}, '${p}', this)">
        <button onclick="document.getElementById('pfile_${alumnoId}_${p.replace(/[^a-zA-Z0-9]/g, '_')}').click()" style="background:#4f46e5;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;">
          <i class="fas fa-upload"></i> Subir
        </button>
      </div>
    `;
    notasContainer.appendChild(row);
  }

  const btnEditAnios = document.getElementById('btnEditAnios');
  if (btnEditAnios) {
    btnEditAnios.style.display = hasAnyNote ? 'inline-block' : 'none';
    btnEditAnios.innerHTML = '<i class="fas fa-edit"></i> Editar Años';
    btnEditAnios.dataset.editing = 'false';
  }
}

async function toggleEditAnios() {
  const btn = document.getElementById('btnEditAnios');
  if (!btn || !perfilAlumnoActual) return;
  const isEditing = btn.dataset.editing === 'true';

  const inputs = document.querySelectorAll('#perfilNotas .anio-input');
  
  if (!isEditing) {
    // Enable editing
    btn.dataset.editing = 'true';
    btn.innerHTML = '<i class="fas fa-save"></i> Guardar Años';
    btn.style.background = '#10b981';
    inputs.forEach(input => input.disabled = false);
  } else {
    // Save changes
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    const periodosAnios = {};
    inputs.forEach(input => {
      periodosAnios[input.dataset.periodo] = input.value.trim();
    });

    const res = await eel.update_anios(perfilAlumnoActual.id, periodosAnios)();
    
    btn.disabled = false;
    if (res.success) {
      openPerfil(perfilAlumnoActual.id);
    } else {
      alert('Error guardando años: ' + res.error);
      btn.dataset.editing = 'false';
      btn.innerHTML = '<i class="fas fa-edit"></i> Editar Años';
      btn.style.background = '#f59e0b';
      inputs.forEach(input => input.disabled = true);
    }
  }
}

async function deleteFromProfile() {
  if (!perfilAlumnoActual) return;
  if (!confirm('\u00bfEliminar a ' + perfilAlumnoActual.nombre + ' ' + perfilAlumnoActual.apellido + ' y todos sus archivos?')) return;
  const res = await eel.delete_alumno(parseInt(perfilAlumnoActual.id))();
  if (res.success) {
    perfilModal.classList.remove('show');
    perfilAlumnoActual = null;
    renderDashboard();
  } else {
    alert('Error al eliminar: ' + res.error);
  }
}

async function uploadFileFromPerfil(alumnoId, periodo, inputEl) {
  const file = inputEl.files[0];
  if (!file) return;
  const anioInputId = `panio_${alumnoId}_${periodo.replace(/[^a-zA-Z0-9]/g, '_')}`;
  const anioInput = document.getElementById(anioInputId);
  const anio = anioInput ? anioInput.value.trim() : new Date().getFullYear().toString();

  const reader = new FileReader();
  reader.onload = async function() {
    const base64 = reader.result;
    const parentDiv = inputEl.closest('div[style]');
    const uploadBtn = parentDiv ? Array.from(parentDiv.querySelectorAll('button')).pop() : null;
    if (uploadBtn) uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    const res = await eel.upload_nota(alumnoId, periodo, base64, file.name, anio)();
    if (res.success) {
      openPerfil(alumnoId);
    } else {
      alert('Error subiendo el archivo: ' + res.error);
    }
  };
  reader.readAsDataURL(file);
}

async function verArchivo(alumnoId, periodo) {
  const res = await eel.open_nota_file(alumnoId, periodo)();
  if (!res.success) {
    alert('No se pudo abrir el archivo: ' + res.error);
  }
}

// ============ HAMBURGER ============
hamburger.addEventListener('click', () => {
  sidebar.classList.toggle('open');
});

document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !hamburger.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});

// ============ INIT ============
showScreen('login');
