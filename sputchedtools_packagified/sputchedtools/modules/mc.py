# -------------MINECRAFT-VERSIONING-LOL-------------

import asyncio
from re import findall
from .aio import get
from ..core import enhance_loop

from typing import Union, Iterable

__all__ = ['MC_VersionList', 'MC_Versions']

class MC_VersionList:
	def __init__(self, versions: list[str], indices: list[int]):
		self.length = len(versions)

		if self.length != len(indices):
			raise ValueError

		self.versions = versions
		self.indices = indices
		# self.map = {version: index for version, index in zip(versions, indices)}

class MC_Versions:
	def __init__(self):

		self.manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

		# Pattern for a single version
		version_pattern = r'1\.\d+(?:\.\d+){0,1}'
		# Pattern for a single version or a version range
		item_pattern = rf'{version_pattern}(?:\s*-\s*{version_pattern})*'
		# Full pattern allowing multiple items separated by commas
		self.full_pattern = rf'{item_pattern}(?:,\s*{item_pattern})*'

		try:
			loop = asyncio.get_event_loop()
		except(RuntimeError, DeprecationWarning):
			enhance_loop()
			loop = asyncio.new_event_loop()

		loop.run_until_complete(self.fetch_version_manifest())
		self.latest = self.release_versions[-1]

	def sort(self, mc_vers: Iterable[str]) -> MC_VersionList:
		filtered_vers = set()

		for ver in mc_vers:
			if not ver: continue

			try:
				filtered_vers.add(
					self.release_versions.index(ver)
				)

			except ValueError:
				continue

		sorted_indices = sorted(filtered_vers)

		return MC_VersionList([self.release_versions[index] for index in sorted_indices], sorted_indices)

	def get_range(self, mc_vers: Union[MC_VersionList, Iterable[str]]) -> str:
		if isinstance(mc_vers, Iterable):
			mc_vers = self.sort(mc_vers)

		version_range = ''
		start = mc_vers.versions[0]  # Start of a potential range
		end = start  # End of the current range

		for i in range(1, mc_vers.length):
			# Check if the current index is a successor of the previous one
			if mc_vers.indices[i] == mc_vers.indices[i - 1] + 1:
				end = mc_vers.versions[i]  # Extend the range
			else:
				# Add the completed range or single version to the result
				if start == end:
					version_range += f'{start}, '
				else:
					version_range += f'{start} - {end}, '
				start = mc_vers.versions[i]  # Start a new range
				end = start

		# Add the final range or single version
		if start == end:
			version_range += start
		else:
			version_range += f'{start} - {end}'

		return version_range

	def get_list(self, mc_vers: str) -> list[str]:
		return findall(self.full_pattern, mc_vers)

	async def fetch_version_manifest(self):
		response = await get(self.manifest_url, toreturn = ['json', 'status'])
		manifest_data, status = response

		if status != 200 or not isinstance(manifest_data, dict):
			raise ConnectionError(f"Couldn't fetch minecraft versions manifest from `{self.manifest_url}`\nStatus: {status}")

		self.release_versions: list[str] = []

		for version in manifest_data['versions']:
			if version['type'] == 'release':
				self.release_versions.append(version['id'])

		self.release_versions.reverse() # Ascending

	def is_version(self, version: str) -> bool:
		try:
			self.release_versions.index(version)
			return True
		except ValueError:
			return False