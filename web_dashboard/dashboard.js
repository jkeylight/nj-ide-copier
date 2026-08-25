class VersionViewer {
    constructor() {
        this.blocks = [];
        this.loadVersions();
    }

    async loadVersions() {
        try {
            const response = await fetch('http://localhost:8765/versions');
            const data = await response.json();
            if (data.status === 'success') {
                this.blocks = data.blocks || [];
                this.render();
            }
        } catch (error) {
            console.error('Failed to load versions:', error);
            document.getElementById('blockList').innerHTML = '<p>Failed to connect to server</p>';
        }
    }

    render() {
        this.renderStats();
        this.renderBlockList();
    }

    renderStats() {
        const totalBlocks = this.blocks.length;
        const totalVersions = this.blocks.reduce((sum, b) => sum + b.versions.length, 0);
        const errorFixes = this.blocks.reduce((sum, b) => sum + b.versions.filter(v => v.status === 'fixed').length, 0);
        const activeBlocks = this.blocks.filter(b => b.versions[b.versions.length - 1]?.status !== 'deprecated').length;

        document.getElementById('totalBlocks').textContent = totalBlocks;
        document.getElementById('totalVersions').textContent = totalVersions;
        document.getElementById('errorFixes').textContent = errorFixes;
        document.getElementById('activeBlocks').textContent = activeBlocks;
    }

    renderBlockList() {
        const blockList = document.getElementById('blockList');
        blockList.innerHTML = '';
        this.blocks.forEach(block => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.cursor = 'pointer';
            card.innerHTML = `<h3>${block.language} - Block ${block.block_id}</h3><p>Versions: ${block.versions.length}</p>`;
            card.onclick = () => this.showBlockDetails(block);
            blockList.appendChild(card);
        });
    }

    showBlockDetails(block) {
        const modal = document.createElement('div');
        modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;justify-content:center;align-items:center;z-index:1000;';
        const content = document.createElement('div');
        content.style.cssText = 'background:white;padding:20px;border-radius:8px;max-width:800px;max-height:80vh;overflow-y:auto;width:90%;';
        let html = `<h2>Block ${block.block_id}</h2><button onclick="this.closest('div[style*=fixed]').remove()" style="float:right">Close</button>`;
        block.versions.forEach(v => {
            html += `<div style="padding:10px;margin:8px 0;background:#f0f0f0;border-radius:4px;"><strong>${v.version_id}</strong> - ${v.status}<br><small>${new Date(v.timestamp * 1000).toLocaleString()}</small></div>`;
        });
        content.innerHTML = html;
        modal.appendChild(content);
        document.body.appendChild(modal);
    }
}

const viewer = new VersionViewer();
